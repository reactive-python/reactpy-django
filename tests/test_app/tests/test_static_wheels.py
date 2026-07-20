"""Tests for ``reactpy_django._static_wheels``.

These tests verify that the wheel-sync logic is safe to run under
multi-process servers (the original concern this module was written
to address) and that it produces a clean, atomic result.
"""

from __future__ import annotations

import json
import threading

import pytest

from reactpy_django import _static_wheels  # noqa: PLC2701


@pytest.fixture
def isolated_dest(tmp_path, monkeypatch):
    """Redirect the destination directory to a temp path for the test.

    We can't just delete the real destination because other tests in
    the suite rely on the wheel being there; we instead point the
    module at a scratch directory via monkeypatch and let it create
    its own lock and marker files there.
    """
    scratch = tmp_path / "wheels"
    monkeypatch.setattr(_static_wheels, "_destination_dir", lambda: scratch)
    return scratch


def test_creates_destination_and_copies_wheel(isolated_dest):
    # First call should copy the wheel into the scratch directory.
    copied = _static_wheels.sync_static_wheels()

    assert copied is True
    wheels = sorted(isolated_dest.glob("reactpy-*-py3-none-any.whl"))
    assert wheels, "expected at least one wheel in the destination"
    # Marker must have been written so subsequent calls are cheap.
    marker = json.loads((isolated_dest / _static_wheels._MARKER_FILE_NAME).read_text())
    assert "wheels" in marker
    assert all("size" in info and "mtime_ns" in info and "sha256" in info for info in marker["wheels"].values())


def test_idempotent_when_marker_matches(isolated_dest):
    _static_wheels.sync_static_wheels()

    # Marker-driven fast path: nothing has changed, so the second
    # call should return False without touching the file lock.
    assert _static_wheels.sync_static_wheels() is False


def test_force_copy_re_runs_even_when_marker_matches(isolated_dest):
    _static_wheels.sync_static_wheels()
    assert _static_wheels.sync_static_wheels(force=True) is True


def test_copies_are_atomic_writes(isolated_dest):
    """The destination wheel must never be observed as a half-written file.

    We simulate a reader racing with a writer by snapshotting the
    destination size while the writer is still mid-stream. If the
    writer is truly atomic (temp + ``os.replace``), the size we read
    will either be 0 (no wheel yet) or the final size — never an
    intermediate value.
    """
    src = _static_wheels._source_dir().glob("reactpy-*-py3-none-any.whl")
    src_wheel = next(src)
    final_size = src_wheel.stat().st_size

    # Snapshot thread: read the size of the destination wheel
    # continuously while the writer runs. Record every observed size.
    observed_sizes: set[int] = set()

    def reader():
        # The destination directory may not exist yet; that's fine —
        # we treat "no file" as size 0.
        for _ in range(200):
            dest_wheels = list(isolated_dest.glob("reactpy-*-py3-none-any.whl"))
            if dest_wheels:
                try:
                    observed_sizes.add(dest_wheels[0].stat().st_size)
                except OSError:
                    # ``os.replace`` may briefly remove the file; treat
                    # as size 0.
                    observed_sizes.add(0)
            else:
                observed_sizes.add(0)

    reader_thread = threading.Thread(target=reader)
    reader_thread.start()

    try:
        _static_wheels.sync_static_wheels(force=True)
    finally:
        reader_thread.join()

    # The reader must only have observed either 0 (no file) or the
    # final size. Any intermediate size proves the write is not atomic.
    assert observed_sizes <= {0, final_size}, f"Reader observed torn writes: sizes={sorted(observed_sizes)}"


def test_lock_serializes_concurrent_workers(isolated_dest):
    """Two threads calling sync_static_wheels concurrently must not corrupt state.

    The advisory lock should serialize the writers so that the marker
    always agrees with what's on disk.
    """
    results: list[bool] = []
    errors: list[BaseException] = []

    def worker():
        try:
            results.append(_static_wheels.sync_static_wheels(force=True))
        except BaseException as exc:  # pragma: no cover - defensive
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"workers raised: {errors}"

    # At least one writer had to do real work. (We don't assert an
    # exact count because the lock may collapse multiple workers into
    # "no-op after first one finishes" — and that's fine.)
    assert any(results) is True

    # Marker must be consistent: every wheel on disk is listed and
    # matches the source fingerprint.
    marker = json.loads((isolated_dest / _static_wheels._MARKER_FILE_NAME).read_text())
    on_disk = {p.name: p.stat().st_size for p in isolated_dest.glob("reactpy-*-py3-none-any.whl")}
    assert set(marker["wheels"].keys()) == set(on_disk.keys())
    for name, info in marker["wheels"].items():
        assert info["size"] == on_disk[name]


def test_prunes_stale_wheels_on_upgrade(isolated_dest):
    """After the source is upgraded, old wheels in the destination are removed."""
    # First copy lands the current wheel.
    _static_wheels.sync_static_wheels()

    # Plant a fake "old" wheel in the destination to simulate an
    # upgrade that left a stale file behind.
    stale = isolated_dest / "reactpy-0.0.0-py3-none-any.whl"
    stale.write_bytes(b"not a real wheel")
    assert stale.exists()

    _static_wheels.sync_static_wheels()

    assert not stale.exists(), "stale wheel should have been pruned"


def test_handles_missing_source_gracefully(tmp_path, monkeypatch):
    """If the installed ReactPy has no wheels (corrupt install), don't crash."""
    fake_src = tmp_path / "empty-static"
    fake_src.mkdir()
    monkeypatch.setattr(_static_wheels, "_source_dir", lambda: fake_src)

    fake_dest = tmp_path / "wheels-dest"
    fake_dest.mkdir()
    monkeypatch.setattr(_static_wheels, "_destination_dir", lambda: fake_dest)

    # Should log a warning and return False instead of raising.
    assert _static_wheels.sync_static_wheels() is False
