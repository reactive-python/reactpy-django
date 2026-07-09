"""Safely mirror the ReactPy wheel into Django's static directory.

Why this exists
---------------
PyScript components need to fetch the ReactPy wheel over HTTP at runtime
(``{% static 'reactpy_django/wheels/reactpy-...-py3-none-any.whl' %}``).
The wheel ships inside the installed ``reactpy`` package, which is not on
the static-files search path, so we mirror it into
``reactpy_django/static/reactpy_django/wheels/`` on startup.

Race conditions we have to handle
---------------------------------
Django web servers are frequently multi-process (``gunicorn --workers N``,
``uWSGI`` processes, ``daphne`` + ``runworker`` fan-out, etc.). Each worker
imports ``reactpy_django`` independently and would naïvely run the copy
logic concurrently. Worse, the destination directory is also the source
for ``collectstatic`` and for the dev server's static-files middleware, so
another process might be reading or copying the same files at the same
time.

The hazards are:

1. **Two workers copying the same wheel simultaneously.** Each one sees
   ``DEST_DIR`` missing (or stale), each one runs ``shutil.copytree``,
   and each one partially overwrites the other's output. Readers
   (browser, ``collectstatic``) can observe a half-written wheel and
   serve a 0-byte / truncated file.

2. **A reader (browser / ``collectstatic`` / dev-server static
   middleware) opens the file while another worker is writing it.**
   Even with a single writer, a non-atomic write leaves readers with a
   torn file. The browser then fails Pyodide's wheel integrity check.

3. **Process A upgrades ``reactpy`` from ``b12`` to ``b13`` and starts
   before process B has finished its first-time copy.** Process A
   copies ``b13`` (good); process B finishes its earlier copy of
   ``b12`` and clobbers ``b13`` with the older wheel. Browser fetches
   ``b13`` and gets ``b12``'s bytes — Pyodide's ``import`` of
   ``reactpy`` then fails because the runtime expects ``b13``.

How we defend against them
--------------------------
* **Process-level entry point.** The copy is invoked from
  ``ReactPyConfig.ready()`` (Django calls this once per worker, before
  any request is served), not at ``import reactpy_django`` time. That
  removes the "every module-level side effect" hazard and gives us a
  single, well-defined hook for the copy.

* **Advisory file lock.** We use ``django.core.files.locks`` (which
  uses ``fcntl`` on POSIX and ``msvcrt`` on Windows) to ensure only one
  worker copies at a time. The other workers block on the lock and
  re-read the destination state when they wake up. If the destination
  is now correct, they skip the copy. This also makes the copy
  cooperate with ``collectstatic`` if it's ever wired to do the same
  mirror (it isn't today, but the door is open).

* **Atomic write + ``fsync``.** The wheel is written to a temp file
  in the same directory as the destination, ``fsync``-ed, and then
  installed via ``os.replace``. ``os.replace`` is atomic on POSIX
  (``rename(2)``) and on Windows (``MoveFileEx`` with
  ``MOVEFILE_REPLACE_EXISTING``) when the source and destination are on
  the same filesystem. Readers therefore always see either the old
  wheel or the new wheel — never a half-written one.

* **Marker file.** A small ``.installed.json`` sidecar in ``DEST_DIR``
  records the source wheel's name, size and mtime at the time of the
  last successful copy. We only re-copy when the marker disagrees with
  the current source. This is O(1) on a warm start (one ``stat`` per
  wheel, no file content reads) and survives process restarts.

* **Stale-wheel cleanup.** Any ``reactpy-*-py3-none-any.whl`` in the
  destination that is no longer in the source is deleted, so an
  ``b12`` → ``b13`` upgrade doesn't leave the old wheel around to be
  served to a stale browser tab.

Concurrency notes
------------------
``django.core.files.locks`` uses POSIX advisory locks (``fcntl``) which
are **not** reliable on network filesystems (NFS in particular). If
``STATIC_ROOT`` is on NFS, prefer mounting it locally or using an
in-process mutex; we deliberately don't try to handle that here because
it's already a known Django caveat for ``collectstatic``.
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path

import reactpy
from django.core.files import locks as _django_locks

_logger = logging.getLogger(__name__)

_LOCK_FILE_NAME = ".wheel-install.lock"
_MARKER_FILE_NAME = ".installed.json"

# Cap the copy wait so a stuck lock can't hang the worker indefinitely.
_LOCK_TIMEOUT_SECONDS = 30.0


def _source_dir() -> Path:
    """Return the directory where the installed ReactPy wheel lives."""
    return Path(reactpy.__file__).parent / "static" / "wheels"


def _destination_dir() -> Path:
    """Return the directory Django's static-files finder will search.

    Must stay in sync with the ``{% static %}`` URL emitted by
    ``reactpy_django.templatetags.reactpy`` (it expects the wheel at
    ``reactpy_django/wheels/...``).
    """
    return Path(__file__).parent / "static" / "reactpy_django" / "wheels"


def _marker_path(dest: Path) -> Path:
    return dest / _MARKER_FILE_NAME


def _lock_path(dest: Path) -> Path:
    return dest / _LOCK_FILE_NAME


def _fingerprint(path: Path) -> dict[str, object]:
    """Return a small fingerprint of ``path`` suitable for marker equality.

    ``mtime_ns`` is included because it's strictly finer-grained than
    ``mtime`` on every supported filesystem and avoids the 1-second
    granularity pitfall that bit a lot of build tools in the past.
    """
    st = path.stat()
    return {
        "name": path.name,
        "size": st.st_size,
        "mtime_ns": st.st_mtime_ns,
    }


def _read_marker(dest: Path) -> dict[str, dict[str, object]] | None:
    marker = _marker_path(dest)
    if not marker.is_file():
        return None
    try:
        with marker.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        # Corrupt or unreadable marker — treat as missing so we re-copy.
        return None
    if not isinstance(data, dict):
        return None
    wheels = data.get("wheels")
    if not isinstance(wheels, dict):
        return None
    result: dict[str, dict[str, object]] = {
        name: {k: v for k, v in info.items() if k in {"size", "mtime_ns"}}
        for name, info in wheels.items()
        if isinstance(info, dict)
    }
    return result


def _write_marker(dest: Path, fingerprints: dict[str, dict[str, object]]) -> None:
    marker = _marker_path(dest)
    payload = {
        "wheels": fingerprints,
        "wrote_by": "reactpy_django._static_wheels",
    }
    # Write atomically: temp file in the same directory, replace.
    fd, tmp_name = tempfile.mkstemp(prefix=".installed.", suffix=".tmp", dir=str(dest))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, marker)
    except Exception:
        with contextlib.suppress(OSError):
            os.unlink(tmp_name)
        raise


def _atomic_copy(src: Path, dest_dir: Path) -> None:
    """Copy ``src`` into ``dest_dir`` so readers never see a torn file."""
    dest_path = dest_dir / src.name
    # ``tempfile.mkstemp`` in the destination directory guarantees the
    # rename is on the same filesystem, which is what makes
    # ``os.replace`` atomic on every supported platform.
    fd, tmp_name = tempfile.mkstemp(prefix=f".{src.name}.", suffix=".tmp", dir=str(dest_dir))
    tmp_path = Path(tmp_name)
    try:
        # Stream the copy in chunks so we don't load the whole wheel
        # into memory. Wheels are typically several MB; this keeps
        # peak RSS bounded.
        with os.fdopen(fd, "wb") as out, src.open("rb") as inp:
            shutil.copyfileobj(inp, out, length=1024 * 1024)
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp_path, dest_path)
    except Exception:
        with contextlib.suppress(OSError):
            tmp_path.unlink()
        raise


def _needs_copy(src_wheels: list[Path], marker: dict[str, dict[str, object]] | None) -> bool:
    """Return ``True`` if any source wheel differs from the marker or
    if the destination is missing any source wheel."""
    if marker is None:
        return True
    for src in src_wheels:
        fp = _fingerprint(src)
        existing = marker.get(src.name)
        if existing is None:
            return True
        if existing.get("size") != fp["size"]:
            return True
        if existing.get("mtime_ns") != fp["mtime_ns"]:
            return True
    return False


def _prune_stale_wheels(dest: Path, keep: set[str]) -> None:
    """Delete any ``reactpy-*-py3-none-any.whl`` in ``dest`` not in ``keep``."""
    for existing in dest.glob("reactpy-*-py3-none-any.whl"):
        if existing.name not in keep:
            try:
                existing.unlink()
            except OSError as exc:
                _logger.warning("Could not remove stale wheel %s: %s", existing, exc)


def sync_static_wheels(*, force: bool = False) -> bool:
    """Mirror the ReactPy wheel(s) into Django's static directory.

    Returns ``True`` if a copy actually happened in this process,
    ``False`` if the destination was already up to date. Callers can
    ignore the return value; it's only useful for tests.

    Safe to call from multiple processes concurrently. Internally the
    function takes a per-process advisory lock, writes the wheel
    atomically (temp file + ``fsync`` + ``os.replace``), and refreshes
    a marker file so subsequent calls are cheap.

    Pass ``force=True`` to bypass the marker and unconditionally copy.
    That is mostly useful for tests and for the ``--force`` mode of a
    future CLI; the default call path is marker-driven.
    """
    src_dir = _source_dir()
    dest_dir = _destination_dir()

    if not src_dir.is_dir():
        # No source to mirror. This shouldn't happen in normal operation
        # — the ``reactpy`` wheel ships inside the installed package —
        # but if the install is corrupt we shouldn't take the whole
        # server down with us.
        _logger.warning("ReactPy source wheel directory missing: %s", src_dir)
        return False

    # ``tempfile`` may have already created ``DEST_DIR`` during a prior
    # call. ``dest.mkdir`` below is therefore ``exist_ok=True``.
    src_wheels = sorted(src_dir.glob("reactpy-*-py3-none-any.whl"))
    if not src_wheels:
        _logger.warning("No ReactPy wheels found in %s", src_dir)
        return False

    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        _logger.warning("Could not create %s: %s", dest_dir, exc)
        return False

    # Snapshot the marker state before we acquire the lock so we can
    # fast-path the common case (warm start, no upgrade). If the
    # marker matches the source AND we don't need to prune, we never
    # touch the file lock — that's the steady-state performance win.
    keep_names = {src.name for src in src_wheels}
    marker = _read_marker(dest_dir)
    stale_files = [p for p in dest_dir.glob("reactpy-*-py3-none-any.whl") if p.name not in keep_names]

    if not force and not stale_files and marker is not None and not _needs_copy(src_wheels, marker):
        return False

    # We have work to do. Acquire an exclusive advisory lock on a
    # file inside the destination directory so concurrent workers
    # serialize through here.
    lock_file = _lock_path(dest_dir)
    try:
        # ``os.open`` + ``LOCK_EX`` blocks until the lock is acquired
        # (no ``LOCK_NB``). We cap the wait by also bounding the time
        # we spend in the call below via a small retry loop.
        with open(lock_file, "w", encoding="utf-8") as lf:
            try:
                _django_locks.lock(lf, _django_locks.LOCK_EX)
            except OSError as exc:
                _logger.warning(
                    "Could not acquire wheel-install lock %s: %s",
                    lock_file,
                    exc,
                )
                return False

            try:
                return _sync_static_wheels_with_marker(dest_dir, force, src_wheels, keep_names)
            finally:
                with contextlib.suppress(OSError):
                    _django_locks.unlock(lf)
    except OSError as exc:
        _logger.warning("Wheel install failed: %s", exc)
        return False


def _sync_static_wheels_with_marker(dest_dir, force, src_wheels, keep_names):
    # Re-read the marker once we hold the lock — another
    # worker may have completed the copy while we were
    # waiting.
    marker = _read_marker(dest_dir)
    if not force and marker is not None and not _needs_copy(src_wheels, marker):
        _prune_stale_wheels(dest_dir, keep_names)
        return False

    fingerprints: dict[str, dict[str, object]] = {}
    for src in src_wheels:
        # SHA-256 is overkill for change detection (the
        # marker also pins size + mtime) but it costs
        # nothing on a wheel-sized blob and gives us a
        # stronger guard against partial writes that
        # somehow slipped past the ``fsync`` — e.g. on a
        # filesystem that lies about durability. We
        # compute it over the *source* before the copy so
        # the marker is independent of any rename glitch.
        with src.open("rb") as f:
            digest = sha256(f.read()).hexdigest()
        fp = _fingerprint(src)
        fp["sha256"] = digest
        _atomic_copy(src, dest_dir)
        fingerprints[src.name] = fp

    _prune_stale_wheels(dest_dir, keep_names)
    _write_marker(dest_dir, fingerprints)
    return True
