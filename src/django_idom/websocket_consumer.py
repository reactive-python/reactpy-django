"""Anything used to construct a websocket endpoint"""
import asyncio
import logging
from typing import Any
from urllib.parse import parse_qsl

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.urls import path
from idom.core.dispatcher import dispatch_single_view
from idom.core.layout import Layout, LayoutEvent

from .app_components import get_component, has_component
from .app_settings import IDOM_WEBSOCKET_URL


logger = logging.getLogger(__name__)


def django_idom_websocket_consumer_url(*args, **kwargs):
    """Return a URL resolver for :class:`IdomAsyncWebSocketConsumer`

    While this is relatively uncommon in most Django apps, because the URL of the
    websocket must be defined by the setting ``IDOM_WEBSOCKET_URL``. There's no need
    to allow users to configure the URL themselves
    """
    return path(
        IDOM_WEBSOCKET_URL + "<view_id>/",
        IdomAsyncWebSocketConsumer.as_asgi(),
        *args,
        **kwargs,
    )


class IdomAsyncWebSocketConsumer(AsyncJsonWebsocketConsumer):
    """Communicates with the browser to perform actions on-demand."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
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
        view_id = self.scope["url_route"]["kwargs"]["view_id"]

        if not has_component(view_id):
            logger.warning(f"Uknown IDOM view ID {view_id!r}")
            return

        component_constructor = get_component(view_id)
        component_kwargs = dict(parse_qsl(self.scope["query_string"]))

        try:
            component_instance = component_constructor(**component_kwargs)
        except Exception:
            logger.exception(
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
