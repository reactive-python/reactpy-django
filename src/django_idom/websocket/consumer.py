"""Anything used to construct a websocket endpoint"""
import asyncio
import logging
from typing import Any

import dill as pickle
from channels.auth import login
from channels.db import database_sync_to_async as convert_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from idom.core.layout import Layout, LayoutEvent
from idom.core.serve import serve_json_patch

from django_idom.config import IDOM_REGISTERED_COMPONENTS
from django_idom.hooks import WebsocketContext
from django_idom.types import ComponentParamData, IdomWebsocket
from django_idom.utils import func_has_params


_logger = logging.getLogger(__name__)


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
        from django_idom import models

        dotted_path = self.scope["url_route"]["kwargs"]["dotted_path"]
        uuid = self.scope["url_route"]["kwargs"]["uuid"]

        try:
            component_constructor = IDOM_REGISTERED_COMPONENTS[dotted_path]
        except KeyError:
            _logger.warning(
                f"Attempt to access invalid IDOM component: {dotted_path!r}"
            )
            return

        # Provide developer access to parts of this websocket
        socket = IdomWebsocket(self.scope, self.close, self.disconnect, dotted_path)

        try:
            # Fetch the component's args/kwargs from the database, if needed
            component_args: tuple[Any, ...] = tuple()
            component_kwargs: dict = {}
            if func_has_params(component_constructor):
                params_query = await models.ComponentParams.objects.aget(uuid=uuid)
                component_params: ComponentParamData = pickle.loads(params_query.data)
                component_args = component_params.args
                component_kwargs = component_params.kwargs

            # Generate the initial component instance
            component_instance = component_constructor(
                *component_args, **component_kwargs
            )
        except Exception:
            _logger.exception(
                f"Failed to construct component {component_constructor} "
                f"with parameters {component_kwargs}"
            )
            return

        self._idom_recv_queue = recv_queue = asyncio.Queue()  # type: ignore
        try:
            await serve_json_patch(
                Layout(WebsocketContext(component_instance, value=socket)),
                self.send_json,
                recv_queue.get,
            )
        except Exception:
            await self.close()
            raise
