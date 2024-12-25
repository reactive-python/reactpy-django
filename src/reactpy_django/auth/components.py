from __future__ import annotations

import asyncio
import contextlib
from logging import getLogger
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from django.urls import reverse
from reactpy import component, hooks, html

from reactpy_django.javascript_components import HttpRequest
from reactpy_django.models import SynchronizeSession

if TYPE_CHECKING:
    from django.contrib.sessions.backends.base import SessionBase

_logger = getLogger(__name__)


@component
def session_manager(child: Any):
    """This component can force the client (browser) to switch HTTP sessions,
    making it match the websocket session.

    Used to force persistent authentication between Django's websocket and HTTP stack."""
    from reactpy_django import config

    synchronize_requested, set_synchronize_requested = hooks.use_state(False)
    _, set_rerender = hooks.use_state(uuid4)
    uuid = hooks.use_ref("")
    scope = hooks.use_connection().scope

    @hooks.use_effect(dependencies=[])
    def setup_asgi_scope():
        """Store trigger functions in the websocket scope so that ReactPy-Django's hooks can command
        any relevant actions."""
        scope.setdefault("reactpy", {})
        scope["reactpy"]["synchronize_session"] = synchronize_session
        scope["reactpy"]["rerender"] = rerender

    @hooks.use_effect(dependencies=[synchronize_requested])
    async def synchronize_session_watchdog():
        """This effect will automatically be cancelled if the session is successfully
        switched (via effect dependencies)."""
        if synchronize_requested:
            await asyncio.sleep(config.REACTPY_AUTH_TIMEOUT + 0.1)
            await asyncio.to_thread(
                _logger.warning,
                f"Client did not switch sessions within {config.REACTPY_AUTH_TIMEOUT} (REACTPY_AUTH_TIMEOUT) seconds.",
            )
            set_synchronize_requested(False)

    async def synchronize_session():
        """Entrypoint where the server will command the client to switch HTTP sessions
        to match the websocket session. This function is stored in the websocket scope so that
        ReactPy-Django's hooks can access it."""
        session: SessionBase | None = scope.get("session")
        if not session or not session.session_key:
            return

        # Delete any sessions currently associated with the previous UUID.
        # This exists to fix scenarios where...
        # 1) A component tree performs multiple login commands for different users.
        # 2) A login is requested, but the server failed to respond to the HTTP request.
        if uuid.current:
            with contextlib.suppress(SynchronizeSession.DoesNotExist):
                obj = await SynchronizeSession.objects.aget(uuid=uuid.current)
                await obj.adelete()

        # Create a fresh UUID
        uuid.set_current(str(uuid4()))

        # Begin the process of synchronizing HTTP and websocket sessions
        obj = await SynchronizeSession.objects.acreate(uuid=uuid.current, session_key=session.session_key)
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

    async def rerender():
        """Event that can force a rerender of the entire component tree."""
        set_rerender(uuid4())

    # If needed, synchronize sessions by configuring all relevant session cookies.
    # This is achieved by commanding the client to perform a HTTP request to our session manager endpoint.
    http_request = None
    if synchronize_requested:
        http_request = HttpRequest(
            {
                "method": "GET",
                "url": reverse("reactpy:session_manager", args=[uuid.current]),
                "body": None,
                "callback": synchronize_session_callback,
            },
        )

    return html._(child, http_request)
