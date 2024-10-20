from django.urls import path

from reactpy_django.config import REACTPY_URL_PREFIX

from .consumer import ReactpyAsyncWebsocketConsumer

REACTPY_WEBSOCKET_ROUTE = path(
    f"{REACTPY_URL_PREFIX}/<str:dotted_path>/<uuid:uuid>/<int:has_args>/",
    ReactpyAsyncWebsocketConsumer.as_asgi(),
)
"""A URL path for :class:`ReactpyAsyncWebsocketConsumer`.

Required since the `reverse()` function does not exist for Django Channels, but ReactPy needs
to know the current websocket path.
"""
