# Broken load order, only used for linting
from channels.routing import ProtocolTypeRouter, URLRouter
from reactpy_django import REACTPY_WEBSOCKET_ROUTE

django_asgi_app = ""


# start
from channels.auth import AuthMiddlewareStack  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(URLRouter([REACTPY_WEBSOCKET_ROUTE])),
    }
)
