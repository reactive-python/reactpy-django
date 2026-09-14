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
    flush_task = use_ref(cast("asyncio.Task[None] | None", None))
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
