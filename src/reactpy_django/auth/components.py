from __future__ import annotations

import asyncio
import contextlib
from logging import getLogger
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from django.urls import reverse
from reactpy import component, hooks

from reactpy_django.javascript_components import HttpRequest
from reactpy_django.models import AuthToken

if TYPE_CHECKING:
    from django.contrib.sessions.backends.base import SessionBase

_logger = getLogger(__name__)


@component
def root_manager(child: Any):
    """This component is serves as the parent component for any ReactPy component tree,
    which allows for the management of the entire component tree."""
    scope = hooks.use_connection().scope
    _, set_rerender = hooks.use_state(uuid4)

    @hooks.use_effect(dependencies=[])
    def setup_asgi_scope():
        """Store trigger functions in the websocket scope so that ReactPy-Django's hooks can command
        any relevant actions."""
        scope["reactpy"]["rerender"] = rerender

    def rerender():
        """Event that can force a rerender of the entire component tree."""
        set_rerender(uuid4())

    return child


@component
def auth_manager():
    """This component uses a client-side component alongside an authentication token
    to make the client (browser) to switch the HTTP auth session, to make it match the websocket session.

    Used to force persistent authentication between Django's websocket and HTTP stack."""
    from reactpy_django import config

    sync_needed, set_sync_needed = hooks.use_state(False)
    token = hooks.use_ref("")
    scope = hooks.use_connection().scope

    @hooks.use_effect(dependencies=[])
    def setup_asgi_scope():
        """Store trigger functions in the websocket scope so that ReactPy-Django's hooks can command
        any relevant actions."""
        scope["reactpy"]["synchronize_auth"] = synchronize_auth

    @hooks.use_effect(dependencies=[sync_needed])
    async def synchronize_auth_watchdog():
        """Detect if the client has taken too long to request a auth session synchronization.

        This effect will automatically be cancelled if the session is successfully
        synchronized (via effect dependencies)."""
        if sync_needed:
            await asyncio.sleep(config.REACTPY_AUTH_TOKEN_MAX_AGE + 0.1)
            await asyncio.to_thread(
                _logger.warning,
                f"Client did not switch authentication sessions within {config.REACTPY_AUTH_TOKEN_MAX_AGE} (REACTPY_AUTH_TOKEN_MAX_AGE) seconds.",
            )
            set_sync_needed(False)

    async def synchronize_auth():
        """Event that can command the client to switch HTTP auth sessions (to match the websocket session)."""
        session: SessionBase | None = scope.get("session")
        if not session or not session.session_key:
            return

        # Delete previous token to resolve race conditions where...
        # 1. Login was called multiple times before the first one is completed.
        # 2. Login was called, but the server failed to respond to the HTTP request.
        if token.current:
            with contextlib.suppress(AuthToken.DoesNotExist):
                obj = await AuthToken.objects.aget(value=token.current)
                await obj.adelete()

        # Create a fresh token
        token.set_current(str(uuid4()))

        # Begin the process of synchronizing HTTP and websocket auth sessions
        obj = await AuthToken.objects.acreate(value=token.current, session_key=session.session_key)
        await obj.asave()
        set_sync_needed(True)

    async def synchronize_auth_callback(status_code: int, response: str):
        """This callback acts as a communication bridge, allowing the client to notify the server
        of the status of auth session switch."""
        set_sync_needed(False)
        if status_code >= 300 or status_code < 200:
            await asyncio.to_thread(
                _logger.error,
                f"Client returned unexpected HTTP status code ({status_code}) while trying to synchronize authentication sessions.",
            )

    # If needed, synchronize authenication sessions by configuring all relevant session cookies.
    # This is achieved by commanding the client to perform a HTTP request to our API endpoint
    # that will set any required cookies.
    if sync_needed:
        return HttpRequest(
            {
                "method": "GET",
                "url": reverse("reactpy:auth_manager", args=[token.current]),
                "body": None,
                "callback": synchronize_auth_callback,
            },
        )

    return None
