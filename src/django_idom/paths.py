from django.urls import path

from . import views
from .config import IDOM_WEB_MODULES_URL, IDOM_WEBSOCKET_URL
from .websocket_consumer import IdomAsyncWebSocketConsumer


def idom_websocket_path(*args, **kwargs):
    """Return a URL resolver for :class:`IdomAsyncWebSocketConsumer`

    While this is relatively uncommon in most Django apps, because the URL of the
    websocket must be defined by the setting ``IDOM_WEBSOCKET_URL``. There's no need
    to allow users to configure the URL themselves.
    """
    return path(
        IDOM_WEBSOCKET_URL + "<view_id>/",
        IdomAsyncWebSocketConsumer.as_asgi(),
        *args,
        **kwargs,
    )


def idom_web_modules_path(*args, **kwargs):
    """Return a URL resolver for static web modules required by IDOM

    While this is relatively uncommon in most Django apps, because the URL of the
    websocket must be defined by the setting ``IDOM_WEBSOCKET_URL``. There's no need
    to allow users to configure the URL themselves.
    """
    return path(
        IDOM_WEB_MODULES_URL + "<path:file>",
        views.web_modules_file,
        *args,
        **kwargs,
    )
