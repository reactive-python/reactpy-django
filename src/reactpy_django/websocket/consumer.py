"""Anything used to construct a websocket endpoint"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import traceback
from concurrent.futures import Future
from datetime import timedelta
from threading import Thread
from typing import TYPE_CHECKING, Any, MutableMapping, Sequence
from urllib.parse import parse_qs

import dill as pickle
import orjson
from channels.auth import login
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone
from reactpy.backend.hooks import ConnectionContext
from reactpy.backend.types import Connection, Location
from reactpy.core.layout import Layout
from reactpy.core.serve import serve_layout

from reactpy_django.clean import clean
from reactpy_django.types import ComponentParams

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

_logger = logging.getLogger(__name__)
BACKHAUL_LOOP = asyncio.new_event_loop()


def start_backhaul_loop():
    """Starts the asyncio event loop that will perform component rendering tasks."""
    asyncio.set_event_loop(BACKHAUL_LOOP)
    BACKHAUL_LOOP.run_forever()


BACKHAUL_THREAD = Thread(
    target=start_backhaul_loop, daemon=True, name="ReactPyBackhaul"
)


class ReactpyAsyncWebsocketConsumer(AsyncJsonWebsocketConsumer):
    """Communicates with the browser to perform actions on-demand."""

    async def connect(self) -> None:
        """The browser has connected."""
        from reactpy_django import models
        from reactpy_django.config import (
            REACTPY_AUTH_BACKEND,
            REACTPY_AUTO_RELOGIN,
            REACTPY_BACKHAUL_THREAD,
        )

        await super().connect()

        # Automatically re-login the user, if needed
        user: AbstractUser | None = self.scope.get("user")
        if REACTPY_AUTO_RELOGIN and user and user.is_authenticated and user.is_active:
            try:
                await login(self.scope, user, backend=REACTPY_AUTH_BACKEND)
            except Exception:
                await asyncio.to_thread(
                    _logger.error,
                    "ReactPy websocket authentication has failed!\n"
                    f"{traceback.format_exc()}",
                )
            try:
                await database_sync_to_async(self.scope["session"].save)()
            except Exception:
                await asyncio.to_thread(
                    _logger.error,
                    "ReactPy has failed to save scope['session']!\n"
                    f"{traceback.format_exc()}",
                )

        # Start the component dispatcher
        self.dispatcher: Future | asyncio.Task
        self.threaded = REACTPY_BACKHAUL_THREAD
        self.component_session: models.ComponentSession | None = None
        if self.threaded:
            if not BACKHAUL_THREAD.is_alive():
                await asyncio.to_thread(
                    _logger.debug, "Starting ReactPy backhaul thread."
                )
                BACKHAUL_THREAD.start()
            self.dispatcher = asyncio.run_coroutine_threadsafe(
                self.run_dispatcher(), BACKHAUL_LOOP
            )
        else:
            self.dispatcher = asyncio.create_task(self.run_dispatcher())

    async def disconnect(self, code: int) -> None:
        """The browser has disconnected."""
        from reactpy_django.config import REACTPY_CLEAN_INTERVAL

        self.dispatcher.cancel()

        # Update the component's last_accessed timestamp
        if self.component_session:
            try:
                await self.component_session.asave()
            except Exception:
                await asyncio.to_thread(
                    _logger.error,
                    "ReactPy has failed to save component session!\n"
                    f"{traceback.format_exc()}",
                )

        # Queue a cleanup, if needed
        if REACTPY_CLEAN_INTERVAL is not None:
            try:
                await database_sync_to_async(clean)()
            except Exception:
                await asyncio.to_thread(
                    _logger.error,
                    "ReactPy cleaning failed!\n" f"{traceback.format_exc()}",
                )

        await super().disconnect(code)

    async def receive_json(self, content: Any, **_) -> None:
        """Receive a message from the browser. Typically, messages are event signals."""
        if self.threaded:
            asyncio.run_coroutine_threadsafe(
                self.recv_queue.put(content), BACKHAUL_LOOP
            )
        else:
            await self.recv_queue.put(content)

    @classmethod
    async def decode_json(cls, text_data):
        return orjson.loads(text_data)

    @classmethod
    async def encode_json(cls, content):
        return orjson.dumps(content).decode()

    async def run_dispatcher(self):
        """Runs the main loop that performs component rendering tasks."""
        from reactpy_django import models
        from reactpy_django.config import (
            REACTPY_REGISTERED_COMPONENTS,
            REACTPY_SESSION_MAX_AGE,
        )

        scope = self.scope
        self.dotted_path = dotted_path = scope["url_route"]["kwargs"]["dotted_path"]
        uuid = scope["url_route"]["kwargs"].get("uuid")
        has_args = scope["url_route"]["kwargs"].get("has_args")
        scope["reactpy"] = {"id": str(uuid)}
        query_string = parse_qs(scope["query_string"].decode(), strict_parsing=True)
        http_pathname = query_string.get("http_pathname", [""])[0]
        http_search = query_string.get("http_search", [""])[0]
        self.recv_queue: asyncio.Queue = asyncio.Queue()
        connection = Connection(  # For `use_connection`
            scope=scope,
            location=Location(pathname=http_pathname, search=http_search),
            carrier=self,
        )
        now = timezone.now()
        component_session_args: Sequence[Any] = ()
        component_session_kwargs: MutableMapping[str, Any] = {}

        # Verify the component has already been registered
        try:
            root_component_constructor = REACTPY_REGISTERED_COMPONENTS[dotted_path]
        except KeyError:
            await asyncio.to_thread(
                _logger.warning,
                f"Attempt to access invalid ReactPy component: {dotted_path!r}",
            )
            return

        # Construct the component. This may require fetching the component's args/kwargs from the database.
        try:
            if has_args:
                self.component_session = await models.ComponentSession.objects.aget(
                    uuid=uuid,
                    last_accessed__gt=now - timedelta(seconds=REACTPY_SESSION_MAX_AGE),
                )
                params: ComponentParams = pickle.loads(self.component_session.params)
                component_session_args = params.args
                component_session_kwargs = params.kwargs

            # Generate the initial component instance
            root_component = root_component_constructor(
                *component_session_args, **component_session_kwargs
            )
        except models.ComponentSession.DoesNotExist:
            await asyncio.to_thread(
                _logger.warning,
                f"Component session for '{dotted_path}:{uuid}' not found. The "
                "session may have already expired beyond REACTPY_SESSION_MAX_AGE. "
                "If you are using a custom `host`, you may have forgotten to provide "
                "args/kwargs.",
            )
            return
        except Exception:
            await asyncio.to_thread(
                _logger.error,
                f"Failed to construct component {root_component_constructor} "
                f"with args='{component_session_args}' kwargs='{component_session_kwargs}'!\n"
                f"{traceback.format_exc()}",
            )
            return

        # Start the ReactPy component rendering loop
        with contextlib.suppress(Exception):
            await serve_layout(
                Layout(ConnectionContext(root_component, value=connection)),
                self.send_json,
                self.recv_queue.get,
            )
