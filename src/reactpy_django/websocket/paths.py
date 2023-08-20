from channels.routing import URLRouter  # noqa: E402
from django.urls import path

from reactpy_django.config import REACTPY_URL_PREFIX

from .consumer import ReactpyAsyncWebsocketConsumer

REACTPY_WEBSOCKET_ROUTE = path(
    f"{REACTPY_URL_PREFIX}/<dotted_path>/",
    URLRouter(
        [
            path("<uuid>/", ReactpyAsyncWebsocketConsumer.as_asgi()),
            path("", ReactpyAsyncWebsocketConsumer.as_asgi()),
        ]
    ),
)
"""A URL path for :class:`ReactpyAsyncWebsocketConsumer`.

Required since the `reverse()` function does not exist for Django Channels, but we need
to know the websocket path.
"""

REACTPY_WEBSOCKET_PATH = REACTPY_WEBSOCKET_ROUTE
