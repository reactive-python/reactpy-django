"""Anything used to construct a websocket endpoint"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from concurrent.futures import Future
from datetime import timedelta
from threading import Thread
from typing import Any, MutableMapping, Sequence

import dill as pickle
from channels.auth import login
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone
from reactpy.backend.hooks import ConnectionContext
from reactpy.backend.types import Connection, Location
from reactpy.core.layout import Layout
from reactpy.core.serve import serve_layout

from reactpy_django.types import ComponentParamData, ComponentWebsocket
from reactpy_django.utils import db_cleanup, func_has_args

_logger = logging.getLogger(__name__)
backhaul_loop = asyncio.new_event_loop()


def start_backhaul_loop():
    """Starts the asyncio event loop that will perform component rendering tasks."""
    asyncio.set_event_loop(backhaul_loop)
    backhaul_loop.run_forever()


backhaul_thread = Thread(target=start_backhaul_loop, daemon=True)


class ReactpyAsyncWebsocketConsumer(AsyncJsonWebsocketConsumer):
    """Communicates with the browser to perform actions on-demand."""

    async def connect(self) -> None:
        """The browser has connected."""
        from reactpy_django.config import REACTPY_AUTH_BACKEND, REACTPY_BACKHAUL_THREAD

        await super().connect()

        # Authenticate the user, if possible
        user: Any = self.scope.get("user")
        if user and user.is_authenticated:
            try:
                await login(self.scope, user, backend=REACTPY_AUTH_BACKEND)
            except Exception:
                await asyncio.to_thread(
                    _logger.exception, "ReactPy websocket authentication has failed!"
                )
        elif user is None:
            await asyncio.to_thread(
                _logger.debug,
                "ReactPy websocket is missing AuthMiddlewareStack! "
                "Users will not be accessible within `use_scope` or `use_websocket`!",
            )

        # Save the session, if possible
        if self.scope.get("session"):
            try:
                await database_sync_to_async(self.scope["session"].save)()
            except Exception:
                await asyncio.to_thread(
                    _logger.exception, "ReactPy has failed to save scope['session']!"
                )
        else:
            await asyncio.to_thread(
                _logger.debug,
                "ReactPy websocket is missing SessionMiddlewareStack! "
                "Sessions will not be accessible within `use_scope` or `use_websocket`!",
            )

        # Start the component dispatcher
        self.dispatcher: Future | asyncio.Task
        self.threaded = REACTPY_BACKHAUL_THREAD
        if self.threaded:
            if not backhaul_thread.is_alive():
                await asyncio.to_thread(
                    _logger.debug, "Starting ReactPy backhaul thread."
                )
                backhaul_thread.start()
            self.dispatcher = asyncio.run_coroutine_threadsafe(
                self.run_dispatcher(), backhaul_loop
            )
        else:
            self.dispatcher = asyncio.create_task(self.run_dispatcher())

    async def disconnect(self, code: int) -> None:
        """The browser has disconnected."""
        self.dispatcher.cancel()
        await super().disconnect(code)

    async def receive_json(self, content: Any, **_) -> None:
        """Receive a message from the browser. Typically, messages are event signals."""
        if self.threaded:
            asyncio.run_coroutine_threadsafe(
                self.recv_queue.put(content), backhaul_loop
            )
        else:
            await self.recv_queue.put(content)

    async def run_dispatcher(self):
        """Runs the main loop that performs component rendering tasks."""
        from reactpy_django import models
        from reactpy_django.config import (
            REACTPY_RECONNECT_MAX,
            REACTPY_REGISTERED_COMPONENTS,
        )

        scope = self.scope
        dotted_path = scope["url_route"]["kwargs"]["dotted_path"]
        uuid = scope["url_route"]["kwargs"]["uuid"]
        search = scope["query_string"].decode()
        self.recv_queue: asyncio.Queue = asyncio.Queue()
        connection = Connection(  # For `use_connection`
            scope=scope,
            location=Location(
                pathname=scope["path"],
                search=f"?{search}" if (search and (search != "undefined")) else "",
            ),
            carrier=ComponentWebsocket(self.close, self.disconnect, dotted_path),
        )
        now = timezone.now()
        component_args: Sequence[Any] = ()
        component_kwargs: MutableMapping[str, Any] = {}

        # Verify the component has already been registered
        try:
            component_constructor = REACTPY_REGISTERED_COMPONENTS[dotted_path]
        except KeyError:
            await asyncio.to_thread(
                _logger.warning,
                f"Attempt to access invalid ReactPy component: {dotted_path!r}",
            )
            return

        # Fetch the component's args/kwargs from the database, if needed
        try:
            if func_has_args(component_constructor):
                try:
                    # Always clean up expired entries first
                    await database_sync_to_async(db_cleanup, thread_sensitive=False)()

                    # Get the queries from a DB
                    params_query = await models.ComponentSession.objects.aget(
                        uuid=uuid,
                        last_accessed__gt=now
                        - timedelta(seconds=REACTPY_RECONNECT_MAX),
                    )
                    params_query.last_accessed = timezone.now()
                    await database_sync_to_async(
                        params_query.save, thread_sensitive=False
                    )()
                except models.ComponentSession.DoesNotExist:
                    await asyncio.to_thread(
                        _logger.warning,
                        f"Component session for '{dotted_path}:{uuid}' not found. The "
                        "session may have already expired beyond REACTPY_RECONNECT_MAX.",
                    )
                    return
                component_params: ComponentParamData = pickle.loads(params_query.params)
                component_args = component_params.args
                component_kwargs = component_params.kwargs

            # Generate the initial component instance
            component_instance = component_constructor(
                *component_args, **component_kwargs
            )
        except Exception:
            await asyncio.to_thread(
                _logger.exception,
                f"Failed to construct component {component_constructor} "
                f"with parameters {component_kwargs}",
            )
            return

        # Start the ReactPy component rendering loop
        with contextlib.suppress(Exception):
            await serve_layout(
                Layout(ConnectionContext(component_instance, value=connection)),
                self.send_json,
                self.recv_queue.get,
            )
