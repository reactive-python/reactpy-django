"""
ASGI config for test_app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from django_idom import django_idom_websocket_consumer_url


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_app.settings")

# Fetch ASGI application before importing dependencies that require ORM models.
http_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402


application = ProtocolTypeRouter(
    {
        "http": http_asgi_app,
        "websocket": URLRouter([django_idom_websocket_consumer_url()]),
    }
)
