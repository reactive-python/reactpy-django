???+ summary

    Django-IDOM can be installed from PyPI to an existing **Django project** with minimal configuration.

## Step 0: Set up a Django Project

These docs assumes you have already created [a **Django project**](https://docs.djangoproject.com/en/dev/intro/tutorial01/), which involves creating and installing at least one **Django app**. If not, check out this [9 minute YouTube tutorial](https://www.youtube.com/watch?v=ZsJRXS_vrw0) created by _IDG TECHtalk_.

## Step 1: Install from PyPI

```bash
pip install django-idom
```

## Step 2: Configure [`settings.py`](https://docs.djangoproject.com/en/dev/topics/settings/)

In your settings you will need to add `django_idom` to [`INSTALLED_APPS`](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-INSTALLED_APPS).

=== "settings.py"

    ```python
    INSTALLED_APPS = [
        "django_idom",
        ...
    ]
    ```

??? warning "Enable Django ASGI (Required)"

    Django-IDOM requires ASGI in order to use Websockets.

    If you have not enabled ASGI on your **Django project** yet, you will need to install `channels[daphne]`, add `daphne` to `INSTALLED_APPS`, then set your `ASGI_APPLICATION` variable.

    Read the [Django Channels Docs](https://channels.readthedocs.io/en/stable/installation.html) for more info.

    === "settings.py"

        ```python
        INSTALLED_APPS = [
            "daphne",
            ...
        ]
        ASGI_APPLICATION = "example_project.asgi.application"
        ```

??? note "Configure IDOM settings (Optional)"

    Below are a handful of values you can change within `settings.py` to modify the behavior of IDOM.

    {% include-markdown "../features/settings.md" start="<!--settings-start-->" end="<!--settings-end-->" preserve-includer-indent=false %}

## Step 3: Configure [`urls.py`](https://docs.djangoproject.com/en/dev/topics/http/urls/)

Add IDOM HTTP paths to your `urlpatterns`.

=== "urls.py"

    ```python
    from django.urls import include, path

    urlpatterns = [
        path("idom/", include("django_idom.http.urls")),
        ...
    ]
    ```

## Step 4: Configure [`asgi.py`](https://docs.djangoproject.com/en/dev/howto/deployment/asgi/)

Register IDOM's Websocket using `IDOM_WEBSOCKET_PATH`.

=== "asgi.py"

    ```python
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

??? question "Where is my `asgi.py`?"

    If you do not have an `asgi.py`, follow the [`channels` installation guide](https://channels.readthedocs.io/en/stable/installation.html).
