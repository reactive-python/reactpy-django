from django.urls import path

from . import views
from .config import IDOM_WEB_MODULES_URL, IDOM_WEBSOCKET_URL
from .websocket_consumer import IdomAsyncWebsocketConsumer


IDOM_WEBSOCKET_PATH = path(
    IDOM_WEBSOCKET_URL + "<view_id>/",
    IdomAsyncWebsocketConsumer.as_asgi(),
    name="idom_websocket",
)
"""A URL resolver for :class:`IdomAsyncWebsocketConsumer`

While this is relatively uncommon in most Django apps, because the URL of the
websocket must be defined by the setting ``IDOM_WEBSOCKET_URL``. There's no need
to allow users to configure the URL themselves.
"""


IDOM_WEB_MODULES_PATH = path(
    IDOM_WEB_MODULES_URL + "<path:file>",
    views.web_modules_file,
    name="idom_web_modules",
)
"""A URL resolver for static web modules required by IDOM

While this is relatively uncommon in most Django apps, because the URL of the
websocket must be defined by the setting ``IDOM_WEBSOCKET_URL``. There's no need
to allow users to configure the URL themselves.
"""
