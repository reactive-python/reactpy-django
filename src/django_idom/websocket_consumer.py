"""Anything used to construct a websocket endpoint"""
import asyncio
import json
import logging
import threading
from typing import Any
from urllib.parse import parse_qsl

import janus
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
        # Thread-safe queue
        self._recv_queue = janus.Queue().async_q

        # Run render as thread
        self._disconnected = threading.Event()
        self._dispatcher_thread = threading.Thread(
            target=asyncio.run,
            args=(self._run_dispatch_loop(),),
            daemon=True,
        )
        self._dispatcher_thread.start()

    async def disconnect(self, code: int) -> None:
        self._disconnected.set()
        await self._recv_queue.put(None)
        self._dispatcher_thread.join(timeout=0)

    async def receive_json(self, content: Any, **kwargs: Any) -> None:
        await self._recv_queue.put(LayoutEvent(**content))

    async def _run_dispatch_loop(self):
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

        try:
            await dispatch_single_view(
                Layout(component_instance),
                self.send_json,
                self._recv_queue.get,
            )
        except Exception:
            await self.close()
            self._disconnected.wait()
            if not self._disconnected.is_set():
                raise
