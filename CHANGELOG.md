## [Unreleased]

### Added

- Add `reactpy_django.hooks.use_session_state` hook for persistent state across WebSocket reconnects.
    - State is stored in the ReactPy database, so it survives multi-process deployments and round-robin load balancing across hosts.
    - `settings.py:REACTPY_SESSION_STATE_MODE` to control whether state is scoped per-tab (default) or per-user.
    - `settings.py:REACTPY_SESSION_STATE_SYNC_INTERVAL` to control how frequently state is flushed to the database.
    - `settings.py:REACTPY_SESSION_STATE_MAX_AGE` to control how long stale session state is retained.
    - `settings.py:REACTPY_CLEAN_SESSION_STATE` to control whether stale session state is cleaned up during automatic cleanups.
- Automatically serve ReactPy wheel from Django's static directory when using PyScript.
