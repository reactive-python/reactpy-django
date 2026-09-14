def use_session_state(
    default: Any,
    key: str,
    *,
    save_default: bool = False,
) -> tuple[Any, Callable[[Any], None]]:
    """Persist state across WebSocket reconnects (and, optionally, page reloads).

    This hook stores its value in the ReactPy database so that it can be restored after a
    WebSocket reconnect, which would otherwise reset all in-memory component state. It is
    more robust than in-memory state because it survives multi-process deployments and
    round-robin load balancing across multiple hosts.

    The state's scope is controlled by the ``REACTPY_SESSION_STATE_MODE`` setting:

    - ``"tab"`` (default): state is scoped to the rendered component (a per-tab, per-component
      token that is stable across reconnects). Works for anonymous users without requiring
      ``django.contrib.sessions``.
    - ``"user"``: state is scoped to the authenticated user, falling back to a per-tab token
      for anonymous users.

    Args:
        default: The value to use when no persisted state exists.
        key: A unique identifier for this state slot within the computed scope. Multiple
            ``use_session_state`` hooks in the same component must use distinct keys.

    Kwargs:
        save_default: If ``True``, the ``default`` value will be persisted when no state
            already exists in the database.

    Returns:
        A tuple of ``(state, set_state)``. ``state`` is the current value (loaded from the
        database, or ``default`` if none exists). ``set_state`` updates the in-memory value
        immediately and schedules a debounced database write so that frequently-changing
        values do not hammer the database.

    Note:
        Only serializable data may be stored. Values are serialized with ``dill``, so most
        common Python objects are supported, but objects holding un-picklable resources
        (e.g. open file handles or network connections) will fail.
    """
    from reactpy_django import config

    scope_id = _resolve_session_state_scope_id()

    # In-memory reactive state. This keeps the UI responsive while database writes are
    # debounced in the background.
    state, set_state = use_state(cast("Any", default))
    loaded = use_ref(False)
    # True once the user has written a value; prevents the async DB load from clobbering
    # a concurrent user update.
    user_set = use_ref(False)
    # Latest value written by the user (kept in a ref so cleanup always flushes it).
    latest = use_ref(default)
    # The currently scheduled debounced flush task; retained to prevent GC.
    flush_task = use_ref(None)
    # Keep the current scope/key in refs so the unmount cleanup (which captures the first
    # render's closure) always flushes to the correct scope/key.
    scope_id_ref = use_ref(scope_id)
    key_ref = use_ref(key)

    @use_async_effect(dependencies=[key, scope_id])
    async def load_state() -> None:
        """Load the persisted value from the database once on mount."""
        data = await _get_session_state(scope_id_ref.current, key_ref.current, default)
        if not user_set.current:
            latest.current = data
            set_state(data)
        loaded.current = True
        if save_default and not user_set.current and data == default:
            await _set_session_state(scope_id_ref.current, key_ref.current, data)

    async def flush() -> None:
        """Persist the latest value to the database."""
        await _set_session_state(scope_id_ref.current, key_ref.current, latest.current)

    async def debounced_flush() -> None:
        """Wait for the sync interval and then persist the latest value."""
        try:
            await asyncio.sleep(config.REACTPY_SESSION_STATE_SYNC_INTERVAL)
            await flush()
        finally:
            if flush_task.current is asyncio.current_task():
                flush_task.current = None

    def schedule_flush() -> None:
        """Debounce database writes so rapid state changes coalesce into one write."""
        if flush_task.current is not None and not flush_task.current.done():
            flush_task.current.cancel()
        flush_task.current = asyncio.create_task(debounced_flush())

    @use_callback
    def set_state_and_persist(value: Any) -> None:
        """Update the in-memory state and schedule a debounced database write."""
        user_set.current = True
        latest.current = value
        set_state(value)
        schedule_flush()

    @use_async_effect(dependencies=[])
    async def flush_on_unmount() -> Callable[[], None]:
        """Ensure the latest state is persisted when the component unmounts.

        This is what makes state survive a WebSocket reconnect: the component's layout is
        torn down on disconnect, so we flush any pending write before it is lost.
        """

        def _cleanup() -> None:
            if flush_task.current is not None and not flush_task.current.done():
                flush_task.current.cancel()
            flush_task.current = asyncio.create_task(flush())

        return _cleanup

    return state, set_state_and_persist


def _resolve_session_state_scope_id() -> str:
    """Resolve the stable identity used to scope persistent session state.

    In ``"tab"`` mode this is the rendered component's UUID (stable across reconnects).
    In ``"user"`` mode this is the authenticated user's primary key, falling back to a
    per-tab token for anonymous users so that unauthenticated visitors still get isolated,
    persistent state.
    """
    from reactpy_django import config

    root_id = use_root_id()

    if config.REACTPY_SESSION_STATE_MODE == "user":
        connection = use_connection()
        user = connection.scope.get("user")
        if user is not None and not user.is_anonymous:
            return f"user:{get_pk(user)}"

    return f"tab:{root_id}"
