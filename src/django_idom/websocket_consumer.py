"""Anything used to construct a websocket endpoint"""
import asyncio
from typing import Any

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from idom.core.dispatcher import dispatch_single_view
from idom.core.layout import Layout, LayoutEvent
from idom.core.proto import ComponentConstructor


class IdomAsyncWebSocketConsumer(AsyncJsonWebsocketConsumer):
    """Communicates with the browser to perform actions on-demand."""

    def __init__(
        self, component: ComponentConstructor, *args: Any, **kwargs: Any
    ) -> None:
        self._idom_component_constructor = component
        super().__init__(*args, **kwargs)

    async def connect(self) -> None:
        await super().connect()
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
        self._idom_recv_queue = recv_queue = asyncio.Queue()
        try:
            await dispatch_single_view(
                Layout(self._idom_component_constructor()),
                self.send_json,
                recv_queue.get,
            )
        except Exception:
            await self.close()
            raise
