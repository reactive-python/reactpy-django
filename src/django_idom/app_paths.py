from django.urls import path

from . import views
from .app_settings import IDOM_WEB_MODULES_URL, IDOM_WEBSOCKET_URL
from .websocket_consumer import IdomAsyncWebSocketConsumer


def django_idom_websocket_consumer_path(*args, **kwargs):
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


def django_idom_web_modules_path(*args, **kwargs):
    return path(
        IDOM_WEB_MODULES_URL + "<path:file>",
        views.web_modules_file,
        *args,
        **kwargs,
    )
