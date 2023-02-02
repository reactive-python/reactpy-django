"""Anything used to construct a websocket endpoint"""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any, MutableMapping, Sequence

import dill as pickle
from channels.auth import login
from channels.db import database_sync_to_async as convert_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone
from idom.backend.hooks import ConnectionContext
from idom.backend.types import Connection, Location
from idom.core.layout import Layout
from idom.core.serve import serve_layout

from django_idom.types import ComponentParamData, ComponentWebsocket
from django_idom.utils import db_cleanup, func_has_params


_logger = logging.getLogger(__name__)


class IdomAsyncWebsocketConsumer(AsyncJsonWebsocketConsumer):
    """Communicates with the browser to perform actions on-demand."""

    async def connect(self) -> None:
        from django.contrib.auth.models import AbstractBaseUser

        await super().connect()

        user: AbstractBaseUser = self.scope.get("user")
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

    async def receive_json(self, content: Any, **_) -> None:
        await self._idom_recv_queue.put(content)

    async def _run_dispatch_loop(self):
        from django_idom import models
        from django_idom.config import IDOM_RECONNECT_MAX, IDOM_REGISTERED_COMPONENTS

        scope = self.scope
        dotted_path = scope["url_route"]["kwargs"]["dotted_path"]
        uuid = scope["url_route"]["kwargs"]["uuid"]
        search = scope["query_string"].decode()
        self._idom_recv_queue: asyncio.Queue = asyncio.Queue()
        connection = Connection(  # For `use_connection`
            scope=scope,
            location=Location(
                pathname=scope["path"],
                search=f"?{search}" if (search and (search != "undefined")) else "",
            ),
            carrier=ComponentWebsocket(self.close, self.disconnect, dotted_path),
        )
        now = timezone.now()
        component_args: Sequence[Any] = tuple()
        component_kwargs: MutableMapping[str, Any] = {}

        # Verify the component has already been registered
        try:
            component_constructor = IDOM_REGISTERED_COMPONENTS[dotted_path]
        except KeyError:
            _logger.warning(
                f"Attempt to access invalid IDOM component: {dotted_path!r}"
            )
            return

        # Fetch the component's args/kwargs from the database, if needed
        try:
            if func_has_params(component_constructor):
                try:
                    # Always clean up expired entries first
                    await convert_to_async(db_cleanup)()

                    # Get the queries from a DB
                    params_query = await models.ComponentParams.objects.aget(
                        uuid=uuid,
                        last_accessed__gt=now - timedelta(seconds=IDOM_RECONNECT_MAX),
                    )
                    params_query.last_accessed = timezone.now()
                    await convert_to_async(params_query.save)()
                except models.ComponentParams.DoesNotExist:
                    _logger.warning(
                        f"Browser has attempted to access '{dotted_path}', "
                        f"but the component has already expired beyond IDOM_RECONNECT_MAX. "
                        "If this was expected, this warning can be ignored."
                    )
                    return
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

        # Begin serving the IDOM component
        try:
            await serve_layout(
                Layout(ConnectionContext(component_instance, value=connection)),
                self.send_json,
                self._idom_recv_queue.get,
            )
        except Exception:
            await self.close()
            raise
