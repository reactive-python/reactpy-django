import os

from django.core.asgi import get_asgi_application

# Ensure DJANGO_SETTINGS_MODULE is set properly based on your project name!
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_project.settings")

# Fetch ASGI application before importing dependencies that require ORM models.
django_asgi_app = get_asgi_application()


from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from reactpy_django import REACTPY_WEBSOCKET_ROUTE  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": URLRouter([REACTPY_WEBSOCKET_ROUTE]),
    }
)
