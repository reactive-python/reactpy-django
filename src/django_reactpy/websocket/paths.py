from django.urls import path

from django_reactpy.config import REACTPY_WEBSOCKET_URL

from .consumer import ReactpyAsyncWebsocketConsumer


REACTPY_WEBSOCKET_PATH = path(
    f"{REACTPY_WEBSOCKET_URL}<dotted_path>/<uuid>/",
    ReactpyAsyncWebsocketConsumer.as_asgi(),
)

"""A URL path for :class:`ReactpyAsyncWebsocketConsumer`.

Required in order for ReactPy to know the websocket path.
"""
