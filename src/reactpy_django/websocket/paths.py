from django.urls import path

from reactpy_django.config import REACTPY_URL_PREFIX
from reactpy_django.websocket.consumer import ReactpyAsyncWebsocketConsumer

REACTPY_WEBSOCKET_ROUTE = path(
    f"{REACTPY_URL_PREFIX}/<str:dotted_path>/<uuid:uuid>/<int:has_args>/",
    ReactpyAsyncWebsocketConsumer.as_asgi(),  # type: ignore
)
"""A URL path for :class:`ReactpyAsyncWebsocketConsumer`.

This global exists since there is no way to retrieve (`reverse()`) a Django Channels URL,
but ReactPy-Django needs to know the current websocket path.
"""
