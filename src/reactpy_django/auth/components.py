from __future__ import annotations

import asyncio
import contextlib
from logging import getLogger
from typing import TYPE_CHECKING
from uuid import uuid4

from django.urls import reverse
from reactpy import component, hooks

from reactpy_django.javascript_components import HttpRequest
from reactpy_django.models import SwitchSession

if TYPE_CHECKING:
    from django.contrib.sessions.backends.base import SessionBase

_logger = getLogger(__name__)


@component
def auth_manager():
    """Component that can force the client to switch HTTP sessions to match the websocket session.

    Used to force persistent authentication between Django's websocket and HTTP stack."""
    from reactpy_django import config

    switch_sessions, set_switch_sessions = hooks.use_state(False)
    uuid_ref = hooks.use_ref(str(uuid4()))
    uuid = uuid_ref.current
    scope = hooks.use_connection().scope

    @hooks.use_effect(dependencies=[])
    def setup_asgi_scope():
        """Store a trigger function in websocket scope so that ReactPy-Django's hooks can command a session synchronization."""
        scope.setdefault("reactpy", {})
        scope["reactpy"]["synchronize_session"] = synchronize_session
        print("configure_asgi_scope")

    @hooks.use_effect(dependencies=[switch_sessions])
    async def synchronize_session_timeout():
        """Ensure that the ASGI scope is available to this component."""
        if switch_sessions:
            await asyncio.sleep(config.REACTPY_AUTH_TIMEOUT + 0.1)
            await asyncio.to_thread(
                _logger.warning,
                f"Client did not switch sessions within {config.REACTPY_AUTH_TIMEOUT} (REACTPY_AUTH_TIMEOUT) seconds.",
            )
            set_switch_sessions(False)

    async def synchronize_session():
        """Entrypoint where the server will command the client to switch HTTP sessions
        to match the websocket session. This function is stored in the websocket scope so that
        ReactPy-Django's hooks can access it."""
        print("sync command")
        session: SessionBase | None = scope.get("session")
        if not session or not session.session_key:
            print("sync error")
            return

        # Delete any sessions currently associated with this UUID
        with contextlib.suppress(SwitchSession.DoesNotExist):
            obj = await SwitchSession.objects.aget(uuid=uuid)
            await obj.adelete()

        obj = await SwitchSession.objects.acreate(uuid=uuid, session_key=session.session_key)
        await obj.asave()

        set_switch_sessions(True)

    async def synchronize_session_callback(status_code: int, response: str):
        """This callback acts as a communication bridge between the client and server, notifying the server
        of the client's response to the session switch command."""
        print("callback")
        set_switch_sessions(False)
        if status_code >= 300 or status_code < 200:
            await asyncio.to_thread(
                _logger.warning,
                f"Client returned unexpected HTTP status code ({status_code}) while trying to sychronize sessions.",
            )

    # If a session cookie was generated, send it to the client
    print("render")
    if switch_sessions:
        print("Rendering HTTP request component with UUID ", uuid)
        return HttpRequest(
            {
                "method": "GET",
                "url": reverse("reactpy:switch_session", args=[uuid]),
                "body": None,
                "callback": synchronize_session_callback,
            },
        )
    return None
