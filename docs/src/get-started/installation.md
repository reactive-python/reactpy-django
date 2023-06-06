## Overview

!!! summary "Overview"

    ReactPy-Django can be installed from PyPI to an existing **Django project** with minimal configuration.

## Step 0: Create a Django Project

These docs assumes you have already created [a **Django project**](https://docs.djangoproject.com/en/dev/intro/tutorial01/), which involves creating and installing at least one **Django app**. If not, check out this [9 minute YouTube tutorial](https://www.youtube.com/watch?v=ZsJRXS_vrw0) created by _IDG TECHtalk_.

## Step 1: Install from PyPI

```bash linenums="0"
pip install reactpy-django
```

## Step 2: Configure [`settings.py`](https://docs.djangoproject.com/en/dev/topics/settings/)

In your settings you will need to add `reactpy_django` to [`INSTALLED_APPS`](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-INSTALLED_APPS).

=== "settings.py"

    ```python
    {% include "../../python/configure-installed-apps.py" %}
    ```

??? warning "Enable Django Channels ASGI (Required)"

    ReactPy-Django requires ASGI Websockets from [Django Channels](https://github.com/django/channels).

    If you have not enabled ASGI on your **Django project** yet, you will need to install `channels[daphne]`, add `daphne` to `INSTALLED_APPS`, then set your `ASGI_APPLICATION` variable.

    Read the [Django Channels Docs](https://channels.readthedocs.io/en/stable/installation.html) for more info.

    === "settings.py"

        ```python
        {% include "../../python/configure-channels.py" %}
        ```

??? note "Configure ReactPy settings (Optional)"

    Below are a handful of values you can change within `settings.py` to modify the behavior of ReactPy.

    ```python
    {% include "../../python/settings.py" %}
    ```

## Step 3: Configure [`urls.py`](https://docs.djangoproject.com/en/dev/topics/http/urls/)

Add ReactPy HTTP paths to your `urlpatterns`.

=== "urls.py"

    ```python
    {% include "../../python/configure-urls.py" %}
    ```

## Step 4: Configure [`asgi.py`](https://docs.djangoproject.com/en/dev/howto/deployment/asgi/)

Register ReactPy's Websocket using `REACTPY_WEBSOCKET_PATH`.

=== "asgi.py"

    ```python
    {% include "../../python/configure-asgi.py" %}
    ```

??? question "Where is my `asgi.py`?"

    If you do not have an `asgi.py`, follow the [`channels` installation guide](https://channels.readthedocs.io/en/stable/installation.html).

## Step 5: Run Migrations

Run Django's database migrations to initialize ReactPy-Django's database table.

```bash linenums="0"
python manage.py migrate
```
