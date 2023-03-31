"""
ASGI config for test_app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_app.settings")

# Fetch ASGI application before importing dependencies that require ORM models.
http_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.sessions import SessionMiddlewareStack  # noqa: E402

from reactpy_django import REACTPY_WEBSOCKET_PATH  # noqa: E402


application = ProtocolTypeRouter(
    {
        "http": http_asgi_app,
        "websocket": SessionMiddlewareStack(
            AuthMiddlewareStack(URLRouter([REACTPY_WEBSOCKET_PATH]))
        ),
    }
)
