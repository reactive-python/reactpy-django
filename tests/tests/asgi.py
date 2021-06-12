"""
ASGI config for tests project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.conf.urls import url
from django.core.asgi import get_asgi_application

from .views import HelloWorld

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

# Fetch ASGI application before importing dependencies that require ORM models.
http_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter

from django_idom import IdomAsyncWebSocketConsumer

application = ProtocolTypeRouter(
    {
        "http": http_asgi_app,
        "websocket": URLRouter(
            [url("", IdomAsyncWebSocketConsumer.as_asgi(component=HelloWorld))]
        ),
    }
)
