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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    async def connect(self) -> None:
        await super().connect()

        self.view_id = self.scope["url_route"]["kwargs"]["view_id"]

        user = self.scope.get("user")
        if user and user.is_authenticated:
            try:
                await login(self.scope, user)
                await convert_to_async(self.scope["session"].save)()
            except Exception:
                _logger.exception("IDOM websocket authentication has failed!")
        elif user is None:
            _logger.warning("IDOM websocket is missing AuthMiddlewareStack!")

        # Limit developer control this websocket
        self.socket = WebsocketConnection(
            self.scope, self.close, self.disconnect, self.view_id
        )

        self._idom_dispatcher_future = asyncio.ensure_future(self._run_dispatch_loop())

    async def disconnect(self, code: int) -> None:
        if self._idom_dispatcher_future.done():
            await self._idom_dispatcher_future
        else:
            self._idom_dispatcher_future.cancel()
        await super().disconnect(code)

    async def receive_json(self, content: Any, **kwargs: Any) -> None:
        await self._idom_recv_queue.put(LayoutEvent(**content))

    async def _run_dispatch_loop(self):

        try:
            component_constructor = IDOM_REGISTERED_COMPONENTS[self.view_id]
        except KeyError:
            _logger.warning(f"Unknown IDOM view ID {self.view_id!r}")
            return

        query_dict = dict(parse_qsl(self.scope["query_string"].decode()))
        component_kwargs = json.loads(query_dict.get("kwargs", "{}"))

        try:
            component_instance = component_constructor(self.socket, **component_kwargs)
        except Exception:
            _logger.exception(
                f"Failed to construct component {component_constructor} "
                f"with parameters {component_kwargs}"
            )
            return

        self._idom_recv_queue = recv_queue = asyncio.Queue()
        try:
            await dispatch_single_view(
                Layout(component_instance),
                self.send_json,
                recv_queue.get,
            )
        except Exception:
            await self.close()
            raise
