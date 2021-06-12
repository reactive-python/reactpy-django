"""Anything used to construct a websocket endpoint"""
import asyncio
from typing import Any

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from idom.core.dispatcher import dispatch_single_view
from idom.core.component import ComponentConstructor


class IdomAsyncWebSocketConsumer(AsyncJsonWebsocketConsumer):
    """Communicates with the browser to perform actions on-demand."""

    def __init__(
        self, component: ComponentConstructor, *args: Any, **kwargs: Any
    ) -> None:
        self._idom_component_constructor = component
        super().__init__(*args, **kwargs)

    async def connect(self) -> None:
        self._idom_recv_queue = recv_queue = asyncio.Queue()
        self._idom_dispatcher_future = dispatch_single_view(
            self._idom_component_constructor,
            self.send_json,
            recv_queue.get,
        )

    async def close(self, *args: Any, **kwargs: Any) -> None:
        self._idom_dispatcher_future.cancel()
        await asyncio.wait([self._idom_dispatcher_future])
        super().close(*args, **kwargs)

    async def receive_json(self, content: Any, **kwargs: Any) -> None:
        await self._idom_recv_queue.put(content)
