???+ tip "Learning Django first is recommended!"

    <!--dj-proj-start-->These docs assumes you have created [a basic **Django project**](https://docs.djangoproject.com/en/dev/intro/tutorial01/), which involves creating and installing at least one **Django app**. If not, check out this [9 minute YouTube tutorial](https://www.youtube.com/watch?v=ZsJRXS_vrw0) created by _IDG TECHtalk_.<!--dj-proj-end-->

## Install from PyPI

```bash
pip install django-idom
```

You'll also need to modify a few files in your **Django project**...

---

## Configure [`settings.py`](https://docs.djangoproject.com/en/dev/topics/settings/)

In your settings you'll need to add `django_idom` to [`INSTALLED_APPS`](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-INSTALLED_APPS).

=== "settings.py"

    ```python linenums="1"
    INSTALLED_APPS = [
        "django_idom",
        ...
    ]
    ```

??? warning "Enable Django ASGI (Required)"

    Django-IDOM requires ASGI in order to use Websockets.

    If you haven't enabled ASGI on your **Django project** yet, you'll need to add `channels` to `INSTALLED_APPS` and set your `ASGI_APPLICATION` variable.

    Read the [Django Channels Docs](https://channels.readthedocs.io/en/stable/installation.html) for more info.

    === "settings.py"

        ```python linenums="1"
        INSTALLED_APPS = [
            "channels",
            ...
        ]
        ASGI_APPLICATION = "example_project.asgi.application"
        ```

??? note "Configure IDOM settings (Optional)"

    Below are a handful of values you can change within `settings.py` to modify the behavior of IDOM.

    {% include-markdown "../features/settings.md" start="<!--settings-start-->" end="<!--settings-end-->" %}

---

## Configure [`urls.py`](https://docs.djangoproject.com/en/dev/topics/http/urls/)

Add IDOM HTTP paths to your `urlpatterns`.

=== "urls.py"

    ```python linenums="1"
    from django.urls import include, path

    urlpatterns = [
        path("idom/", include("django_idom.http.urls")),
        ...
    ]
    ```

---

## Configure [`asgi.py`](https://docs.djangoproject.com/en/dev/howto/deployment/asgi/)

Register IDOM's Websocket using `IDOM_WEBSOCKET_PATH`.

=== "asgi.py"

    ```python linenums="1"
    import os
    from django.core.asgi import get_asgi_application

    # Ensure DJANGO_SETTINGS_MODULE is set properly based on your project name!
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_project.settings")
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

??? question "Where is my asgi.py?"

    If you do not have an `asgi.py`, follow the [`channels` installation guide](https://channels.readthedocs.io/en/stable/installation.html).
