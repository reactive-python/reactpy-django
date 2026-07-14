"""Anything used to construct a websocket endpoint"""

from __future__ import annotations

import asyncio
import contextlib
import copy
import logging
import traceback
from datetime import timedelta
from threading import Thread
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import parse_qs

import dill
import orjson
from channels.auth import login
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone
from reactpy.core.hooks import ConnectionContext
from reactpy.core.layout import Layout
from reactpy.core.serve import serve_layout
from reactpy.types import Connection, Location

from reactpy_django.tasks import clean
from reactpy_django.utils import ensure_async

if TYPE_CHECKING:
    from collections.abc import MutableMapping, Sequence
    from concurrent.futures import Future

    from reactpy_django import models
    from reactpy_django.types import ComponentParams

_logger = logging.getLogger(__name__)
BACKHAUL_LOOP = asyncio.new_event_loop()


def start_backhaul_loop():
    """Starts the asyncio event loop that will perform component rendering tasks."""
    asyncio.set_event_loop(BACKHAUL_LOOP)
    BACKHAUL_LOOP.run_forever()


BACKHAUL_THREAD = Thread(target=start_backhaul_loop, daemon=True, name="ReactPyBackhaul")


class ReactpyAsyncWebsocketConsumer(AsyncJsonWebsocketConsumer):
    """Communicates with the browser to perform actions on-demand.

    Uses a single WebSocket connection per client webpage to serve
    multiple ReactPy components, reducing connection overhead.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Shared state across all components on this WebSocket
        self.threaded: bool = False
        self.component_queues: dict[str, asyncio.Queue] = {}
        self.component_sessions: dict[str, models.ComponentSession | None] = {}
        self.component_tasks: dict[str, Future | asyncio.Task] = {}
        self.page_path: str = ""
        self.page_query_string: str = ""

    async def connect(self) -> None:
        """The browser has connected."""
        from reactpy_django.config import (
            REACTPY_AUTH_BACKEND,
            REACTPY_AUTO_RELOGIN,
            REACTPY_BACKHAUL_THREAD,
        )

        await super().connect()

        # Parse page-level info from query string (shared across all components)
        query_string = parse_qs(self.scope["query_string"].decode(), strict_parsing=True)
        self.page_path = query_string.get("path", [""])[0] or "/"
        self.page_query_string = query_string.get("qs", [""])[0]

        # Automatically re-login the user, if needed
        user = self.scope.get("user")
        if REACTPY_AUTO_RELOGIN and user and user.is_authenticated and user.is_active:
            try:
                await login(self.scope, user, backend=REACTPY_AUTH_BACKEND)  # type: ignore[reportArgumentType]
            except Exception:
                await asyncio.to_thread(
                    _logger.error,
                    f"ReactPy websocket authentication has failed!\n{traceback.format_exc()}",
                )
            try:
                await ensure_async(self.scope["session"].save)()  # type: ignore[reportTypedDictNotRequiredAccess]
            except Exception:
                await asyncio.to_thread(
                    _logger.error,
                    f"ReactPy has failed to save scope['session']!\n{traceback.format_exc()}",
                )

        # No longer starting a single dispatcher — each component gets its own
        # rendering task when a "mount-component" message is received.
        self.threaded = REACTPY_BACKHAUL_THREAD
        self.scope["reactpy"] = {"id": str(id(self))}  # type: ignore[reportGeneralTypeIssues]

    async def disconnect(self, code: int) -> None:
        """The browser has disconnected."""
        from reactpy_django.config import REACTPY_CLEAN_INTERVAL

        # Cancel all running component rendering tasks
        for task in self.component_tasks.values():
            task.cancel()
        self.component_tasks.clear()

        # Save all component sessions
        for session in self.component_sessions.values():
            if session:
                try:
                    await session.asave()
                except Exception:
                    await asyncio.to_thread(
                        _logger.error,
                        f"ReactPy has failed to save component session!\n{traceback.format_exc()}",
                    )
        self.component_sessions.clear()
        self.component_queues.clear()

        # Queue a cleanup, if needed
        if REACTPY_CLEAN_INTERVAL is not None:
            try:
                await ensure_async(clean)()
            except Exception:
                await asyncio.to_thread(
                    _logger.error,
                    f"ReactPy cleaning failed!\n{traceback.format_exc()}",
                )

        await super().disconnect(code)

    async def receive_json(self, content: Any, **_) -> None:
        """Receive a message from the browser.

        Handles two message types:
        - ``mount-component``: Start a new component rendering task.
        - ``layout-event`` (rootId present): Route the event to the
          specific component's event queue.
        """
        if content.get("type") == "mount-component":
            if self.threaded:
                if not BACKHAUL_THREAD.is_alive():
                    await asyncio.to_thread(_logger.debug, "Starting ReactPy backhaul thread.")
                    BACKHAUL_THREAD.start()

                future: Future = asyncio.run_coroutine_threadsafe(self._run_component(content), BACKHAUL_LOOP)
                self.component_tasks[content["rootId"]] = future
            else:
                task = asyncio.create_task(self._run_component(content))
                self.component_tasks[content["rootId"]] = task
        elif content.get("rootId"):
            root_id = content["rootId"]
            if root_id in self.component_queues:
                if self.threaded:
                    asyncio.run_coroutine_threadsafe(self.component_queues[root_id].put(content), BACKHAUL_LOOP)
                else:
                    await self.component_queues[root_id].put(content)

    @classmethod
    async def decode_json(cls, text_data):
        return orjson.loads(text_data)

    @classmethod
    async def encode_json(cls, content):
        return orjson.dumps(content).decode()

    async def _run_component(self, content: dict[str, Any]) -> None:
        """Construct a component and run its ``serve_layout`` loop.

        Each component gets its own event queue, isolated scope, and runs
        independently within the shared WebSocket connection. Layout updates
        are tagged with a ``rootId`` so the client can route them to the
        correct component.
        """
        from reactpy_django import models
        from reactpy_django.auth.components import auth_manager, root_manager
        from reactpy_django.config import (
            REACTPY_REGISTERED_COMPONENTS,
            REACTPY_SESSION_MAX_AGE,
        )

        root_id: str = content["rootId"]
        dotted_path: str = content["dottedPath"]
        uuid: str = content.get("componentUuid", root_id)
        has_args: bool = content.get("hasArgs", False)

        # Maintain backward compatibility for user code that checks
        # ws.carrier.dotted_path
        self.dotted_path = dotted_path

        # Each component needs its own isolated scope copy to prevent concurrent
        # component tasks from overwriting each other's scope["reactpy"] entries.
        scope = copy.copy(self.scope)
        scope["reactpy"] = {"id": str(uuid)}  # type: ignore[reportGeneralTypeIssues]
        now = timezone.now()
        component_session_args: Sequence[Any] = ()
        component_session_kwargs: MutableMapping[str, Any] = {}

        connection = Connection(
            scope=cast("dict[str, Any]", scope),
            location=Location(path=self.page_path, query_string=self.page_query_string),
            carrier=self,
        )

        # Verify the component has already been registered
        try:
            root_component_constructor = REACTPY_REGISTERED_COMPONENTS[dotted_path]
        except KeyError:
            await asyncio.to_thread(
                _logger.warning,
                f"Attempt to access invalid ReactPy component: {dotted_path!r}",
            )
            return

        # Construct the component. This may require fetching the component's
        # args/kwargs from the database.
        try:
            if has_args:
                component_session = await models.ComponentSession.objects.aget(
                    uuid=uuid,
                    last_accessed__gt=now - timedelta(seconds=REACTPY_SESSION_MAX_AGE),
                )
                params: ComponentParams = dill.loads(component_session.params)
                component_session_args = params.args
                component_session_kwargs = params.kwargs
                self.component_sessions[root_id] = component_session

            root_component = root_component_constructor(*component_session_args, **component_session_kwargs)
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

        # Create a dedicated event queue for this component
        recv_queue: asyncio.Queue = asyncio.Queue()
        self.component_queues[root_id] = recv_queue

        # Wrap outgoing messages with the rootId so the client can route them
        async def send_wrapper(message: Any) -> None:
            message["rootId"] = root_id
            await self.send_json(message)

        # Start the ReactPy component rendering loop
        with contextlib.suppress(Exception):
            await serve_layout(
                Layout(
                    ConnectionContext(
                        auth_manager(),
                        root_manager(root_component),
                        value=connection,
                    )
                ),
                send_wrapper,
                recv_queue.get,
            )

        # Cleanup after the component rendering loop finishes
        self.component_queues.pop(root_id, None)
        self.component_sessions.pop(root_id, None)
        self.component_tasks.pop(root_id, None)
