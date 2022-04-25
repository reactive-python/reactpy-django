## Install from PyPI

```bash
pip install django-idom
```

You'll also need to modify a few files in your Django project...

---

## Configure [`settings.py`](https://docs.djangoproject.com/en/dev/topics/settings/)

In your settings you'll need to add `django_idom` to [`INSTALLED_APPS`](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-INSTALLED_APPS).

```python title="settings.py"
INSTALLED_APPS = [
    "django_idom",
    ...
]
```

!!! note "Optional: Configure IDOM settings"

        ```python title="settings.py"
        # If "idom" cache is not configured, then we'll use "default" instead
        CACHES = {
        "idom": {"BACKEND": ...},
        }

        # Maximum seconds between two reconnection attempts that would cause the client give up.
        # 0 will disable reconnection.
        IDOM_WS_MAX_RECONNECT_TIMEOUT = 604800

        # The URL for IDOM to serve websockets
        IDOM_WEBSOCKET_URL = "idom/"
        ```

!!! note "Note: Configuring New Django Projects"

        If you haven't enabled ASGI on your Django project yet, don't forget to add `channels` to `INSTALLED_APPS` and set your `ASGI_APPLICATION`.
        ```python title="settings.py"
        INSTALLED_APPS = [..., "channels", ...]
        ASGI_APPLICATION = "my_django_project.asgi.application"
        ```

---

## Configure [`urls.py`](https://docs.djangoproject.com/en/dev/topics/http/urls/)

Add IDOM HTTP paths to your `urlpatterns`.

```python title="urls.py"
from django.urls import include, path

urlpatterns = [
    path("idom/", include("django_idom.http.urls")),
    ...
]
```

---

## Configure [`asgi.py`](https://docs.djangoproject.com/en/dev/howto/deployment/asgi/)

Register IDOM's Websocket using `IDOM_WEBSOCKET_PATH`.

```python title="asgi.py"
import os
from django.core.asgi import get_asgi_application

# Ensure DJANGO_SETTINGS_MODULE is set properly based on your project name!
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_django_project.settings")
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from django_idom import IDOM_WEBSOCKET_PATH

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": SessionMiddlewareStack(
            AuthMiddlewareStack(URLRouter([IDOM_WEBSOCKET_PATH]))
        ),
    }
)
```

!!! note "Note: Locating `asgi.py`"

    If you do not have an `asgi.py`, follow the [`channels` installation guide](https://channels.readthedocs.io/en/stable/installation.html).