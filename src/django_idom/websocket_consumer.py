"""Anything used to construct a websocket endpoint"""
import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional
from urllib.parse import parse_qsl

from channels.auth import login
from channels.db import database_sync_to_async as convert_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from idom.core.dispatcher import dispatch_single_view
from idom.core.layout import Layout, LayoutEvent

from .config import IDOM_REGISTERED_COMPONENTS


_logger = logging.getLogger(__name__)


@dataclass
class WebsocketConnection:
    scope: dict
    close: Callable[[Optional[int]], Awaitable[None]]
    disconnect: Callable[[int], Awaitable[None]]
    view_id: str


class IdomAsyncWebsocketConsumer(AsyncJsonWebsocketConsumer):
    """Communicates with the browser to perform actions on-demand."""

    async def connect(self) -> None:
        await super().connect()

        user = self.scope.get("user")
        if user and user.is_authenticated:
            try:
                await login(self.scope, user)
                await convert_to_async(self.scope["session"].save)()
            except Exception:
                _logger.exception("IDOM websocket authentication has failed!")
        elif user is None:
            _logger.warning("IDOM websocket is missing AuthMiddlewareStack!")

        self._dispatcher_future = asyncio.ensure_future(self._run_dispatch_loop())

    async def disconnect(self, code: int) -> None:
        if self._dispatcher_future.done():
            await self._dispatcher_future
        else:
            self._dispatcher_future.cancel()
        await super().disconnect(code)

    async def receive_json(self, content: Any, **kwargs: Any) -> None:
        await self._recv_queue.put(LayoutEvent(**content))

    async def _run_dispatch_loop(self):
        view_id = self.scope["url_route"]["kwargs"]["view_id"]

        try:
            component_constructor = IDOM_REGISTERED_COMPONENTS[view_id]
        except KeyError:
            _logger.warning(f"Unknown IDOM view ID {view_id!r}")
            return

        query_dict = dict(parse_qsl(self.scope["query_string"].decode()))
        component_kwargs = json.loads(query_dict.get("kwargs", "{}"))

        # Provide developer access to parts of this websocket
        socket = WebsocketConnection(self.scope, self.close, self.disconnect, view_id)

        try:
            component_instance = component_constructor(socket, **component_kwargs)
        except Exception:
            _logger.exception(
                f"Failed to construct component {component_constructor} "
                f"with parameters {component_kwargs}"
            )
            return

        self._recv_queue = recv_queue = asyncio.Queue()
        try:
            await dispatch_single_view(
                Layout(component_instance),
                self.send_json,
                recv_queue.get,
            )
        except Exception:
            await self.close()
            raise
