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
from reactpy.backend.hooks import ConnectionContext
from reactpy.backend.types import Connection, Location
from reactpy.core.layout import Layout
from reactpy.core.serve import serve_layout

from reactpy_django.types import ComponentParamData, ComponentWebsocket
from reactpy_django.utils import db_cleanup, func_has_params


_logger = logging.getLogger(__name__)


class ReactpyAsyncWebsocketConsumer(AsyncJsonWebsocketConsumer):
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
                _logger.exception("ReactPy websocket authentication has failed!")
        elif user is None:
            _logger.warning("ReactPy websocket is missing AuthMiddlewareStack!")

        self._reactpy_dispatcher_future = asyncio.ensure_future(
            self._run_dispatch_loop()
        )

    async def disconnect(self, code: int) -> None:
        if self._reactpy_dispatcher_future.done():
            await self._reactpy_dispatcher_future
        else:
            self._reactpy_dispatcher_future.cancel()
        await super().disconnect(code)

    async def receive_json(self, content: Any, **_) -> None:
        await self._reactpy_recv_queue.put(content)

    async def _run_dispatch_loop(self):
        from reactpy_django import models
        from reactpy_django.config import (
            REACTPY_DATABASE,
            REACTPY_RECONNECT_MAX,
            REACTPY_REGISTERED_COMPONENTS,
        )

        scope = self.scope
        dotted_path = scope["url_route"]["kwargs"]["dotted_path"]
        uuid = scope["url_route"]["kwargs"]["uuid"]
        search = scope["query_string"].decode()
        self._reactpy_recv_queue: asyncio.Queue = asyncio.Queue()
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
            component_constructor = REACTPY_REGISTERED_COMPONENTS[dotted_path]
        except KeyError:
            _logger.warning(
                f"Attempt to access invalid ReactPy component: {dotted_path!r}"
            )
            return

        # Fetch the component's args/kwargs from the database, if needed
        try:
            if func_has_params(component_constructor):
                try:
                    # Always clean up expired entries first
                    await convert_to_async(db_cleanup)()

                    # Get the queries from a DB
                    params_query = await models.ComponentSession.objects.using(
                        REACTPY_DATABASE
                    ).aget(
                        uuid=uuid,
                        last_accessed__gt=now
                        - timedelta(seconds=REACTPY_RECONNECT_MAX),
                    )
                    params_query.last_accessed = timezone.now()
                    await convert_to_async(params_query.save)()
                except models.ComponentSession.DoesNotExist:
                    _logger.warning(
                        f"Browser has attempted to access '{dotted_path}', "
                        f"but the component has already expired beyond REACTPY_RECONNECT_MAX. "
                        "If this was expected, this warning can be ignored."
                    )
                    return
                component_params: ComponentParamData = pickle.loads(params_query.params)
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

        # Begin serving the ReactPy component
        try:
            await serve_layout(
                Layout(ConnectionContext(component_instance, value=connection)),
                self.send_json,
                self._reactpy_recv_queue.get,
            )
        except Exception:
            await self.close()
            raise
