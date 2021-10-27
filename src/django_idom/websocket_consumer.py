"""Anything used to construct a websocket endpoint"""
import asyncio
import json
import logging
from threading import Thread
from typing import Any
from urllib.parse import parse_qsl

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from idom.core.dispatcher import dispatch_single_view
from idom.core.layout import Layout, LayoutEvent

from .config import IDOM_REGISTERED_COMPONENTS


_logger = logging.getLogger(__name__)


class IdomAsyncWebSocketConsumer(AsyncJsonWebsocketConsumer):
    """Communicates with the browser to perform actions on-demand."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    async def connect(self) -> None:
        await super().connect()
        self._idom_dispatcher_thread: Thread = Thread(target=self._run_dispatch_loop)
        self._idom_dispatcher_thread.daemon = True
        self._idom_dispatcher_thread.start()

    async def disconnect(self, code: int) -> None:
        await self._idom_recv_queue.put(None)
        self._idom_dispatcher_thread.join()
        await super().disconnect(code)

    async def receive_json(self, content: Any, **kwargs: Any) -> None:
        await self._idom_recv_queue.put(LayoutEvent(**content))

    @async_to_sync
    async def _run_dispatch_loop(self):
        while True:
            view_id = self.scope["url_route"]["kwargs"]["view_id"]

            try:
                component_constructor = IDOM_REGISTERED_COMPONENTS[view_id]
            except KeyError:
                _logger.warning(f"Uknown IDOM view ID {view_id!r}")
                return

            query_dict = dict(parse_qsl(self.scope["query_string"].decode()))
            component_kwargs = json.loads(query_dict.get("kwargs", "{}"))

            try:
                component_instance = component_constructor(**component_kwargs)
            except Exception:
                _logger.exception(
                    f"Failed to construct component {component_constructor} "
                    f"with parameters {component_kwargs}"
                )
                return

            self._idom_recv_queue = recv_queue = asyncio.Queue()
            try:
                queue_item = recv_queue.get()
                if queue_item is None:
                    break

                await dispatch_single_view(
                    Layout(component_instance),
                    self.send_json,
                    lambda: queue_item,
                )
            except Exception:
                await self.close()
                raise
