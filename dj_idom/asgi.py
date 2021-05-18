"""
ASGI config for dj_idom project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.conf.urls import url
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj_idom.settings")

# Fetch ASGI application before importing dependencies that require ORM models.
http_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter

from .consumers import CommandConsumer

application = ProtocolTypeRouter(
    {
        "http": http_asgi_app,
        "websocket": URLRouter([url("", CommandConsumer().as_asgi())]),
    }
)
