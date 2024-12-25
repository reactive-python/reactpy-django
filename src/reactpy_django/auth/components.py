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
    scope = hooks.use_connection().scope
    _, set_rerender = hooks.use_state(uuid4)

    @hooks.use_effect(dependencies=[])
    def setup_asgi_scope():
        """Store trigger functions in the websocket scope so that ReactPy-Django's hooks can command
        any relevant actions."""
        scope["reactpy"]["rerender"] = rerender

    async def rerender():
        """Event that can force a rerender of the entire component tree."""
        set_rerender(uuid4())

    return child


@component
def session_manager():
    """This component can force the client (browser) to switch HTTP sessions,
    making it match the websocket session, by using a authentication token.

    Used to force persistent authentication between Django's websocket and HTTP stack."""
    from reactpy_django import config

    synchronize_requested, set_synchronize_requested = hooks.use_state(False)
    token = hooks.use_ref("")
    scope = hooks.use_connection().scope

    @hooks.use_effect(dependencies=[])
    def setup_asgi_scope():
        """Store trigger functions in the websocket scope so that ReactPy-Django's hooks can command
        any relevant actions."""
        scope["reactpy"]["synchronize_session"] = synchronize_session

    @hooks.use_effect(dependencies=[synchronize_requested])
    async def synchronize_session_watchdog():
        """Detected if the client has taken too long to request a session synchronization.

        This effect will automatically be cancelled if the session is successfully
        switched (via effect dependencies)."""
        if synchronize_requested:
            await asyncio.sleep(config.REACTPY_AUTH_TOKEN_TIMEOUT + 0.1)
            await asyncio.to_thread(
                _logger.warning,
                f"Client did not switch sessions within {config.REACTPY_AUTH_TOKEN_TIMEOUT} (REACTPY_AUTH_TOKEN_TIMEOUT) seconds.",
            )
            set_synchronize_requested(False)

    async def synchronize_session():
        """Event that can command the client to switch HTTP sessions (to match the websocket session)."""
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

        # Begin the process of synchronizing HTTP and websocket sessions
        obj = await AuthToken.objects.acreate(value=token.current, session_key=session.session_key)
        await obj.asave()
        set_synchronize_requested(True)

    async def synchronize_session_callback(status_code: int, response: str):
        """This callback acts as a communication bridge, allowing the client to notify the server
        of the status of session switch."""
        set_synchronize_requested(False)
        if status_code >= 300 or status_code < 200:
            await asyncio.to_thread(
                _logger.warning,
                f"Client returned unexpected HTTP status code ({status_code}) while trying to sychronize sessions.",
            )

    # If needed, synchronize sessions by configuring all relevant session cookies.
    # This is achieved by commanding the client to perform a HTTP request to our session manager endpoint.
    if synchronize_requested:
        return HttpRequest(
            {
                "method": "GET",
                "url": reverse("reactpy:session_manager", args=[token.current]),
                "body": None,
                "callback": synchronize_session_callback,
            },
        )

    return None
