## Overview

<p class="intro" markdown>

If you want to add some interactivity to your existing **Django project**, you don't have to rewrite it in ReactPy. Use [ReactPy-Django](https://github.com/reactive-python/reactpy-django) to add [ReactPy](https://github.com/reactive-python/reactpy) to your existing stack, and render interactive components anywhere.

</p>

!!! note

    These docs assumes you have already created [a **Django project**](https://docs.djangoproject.com/en/dev/intro/tutorial01/), which involves creating and installing at least one **Django app**.

    If do not have a **Django project**, check out this [9 minute YouTube tutorial](https://www.youtube.com/watch?v=ZsJRXS_vrw0) created by _IDG TECHtalk_.

---

## Step 1: Install from PyPI

Run the following command to install [`reactpy-django`](https://pypi.org/project/reactpy-django/) in your Python environment.

```bash linenums="0"
pip install reactpy-django
```

## Step 2: Configure `settings.py`

Add `reactpy_django` to [`INSTALLED_APPS`](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-INSTALLED_APPS) in your [`settings.py`](https://docs.djangoproject.com/en/dev/topics/settings/) file.

=== "settings.py"

    ```python
    {% include "../../python/configure-installed-apps.py" %}
    ```

??? warning "Enable Django Channels ASGI (Required)"

    ReactPy-Django requires ASGI Websockets from [Django Channels](https://github.com/django/channels).

    If you have not enabled ASGI on your **Django project** yet, you will need to

    1. Install `channels[daphne]`
    2. Add `daphne` to `INSTALLED_APPS`
    3. Set your `ASGI_APPLICATION` variable.

    === "settings.py"

        ```python
        {% include "../../python/configure-channels.py" %}
        ```

    Consider reading the [Django Channels Docs](https://channels.readthedocs.io/en/stable/installation.html) for more info.

??? note "Configure ReactPy settings (Optional)"

    {% include "../reference/settings.md" start="<!--config-details-start-->" end="<!--config-details-end-->"  %}

## Step 3: Configure `urls.py`

Add ReactPy HTTP paths to your `urlpatterns` in your [`urls.py`](https://docs.djangoproject.com/en/dev/topics/http/urls/) file.

=== "urls.py"

    ```python
    {% include "../../python/configure-urls.py" %}
    ```

## Step 4: Configure `asgi.py`

Register ReactPy's WebSocket using `REACTPY_WEBSOCKET_ROUTE` in your [`asgi.py`](https://docs.djangoproject.com/en/dev/howto/deployment/asgi/) file.

=== "asgi.py"

    ```python
    {% include "../../python/configure-asgi.py" %}
    ```

??? note "Add `AuthMiddlewareStack` and `SessionMiddlewareStack` (Optional)"

    There are many situations where you need to access the Django `User` or `Session` objects within ReactPy components. For example, if you want to:

    1. Access the `User` that is currently logged in
    2. Login or logout the current `User`
    3. Access Django's `Session` object

    In these situations will need to ensure you are using `AuthMiddlewareStack` and/or `SessionMiddlewareStack`.

    ```python linenums="0"
    {% include "../../python/configure-asgi-middleware.py" start="# start" %}
    ```

??? question "Where is my `asgi.py`?"

    If you do not have an `asgi.py`, follow the [`channels` installation guide](https://channels.readthedocs.io/en/stable/installation.html).

## Step 5: Run database migrations

Run Django's [`migrate` command](https://docs.djangoproject.com/en/dev/topics/migrations/) to initialize ReactPy-Django's database table.

```bash linenums="0"
python manage.py migrate
```

## Step 6: Check your configuration

Run Django's [`check` command](https://docs.djangoproject.com/en/dev/ref/django-admin/#check) to verify if ReactPy was set up correctly.

```bash linenums="0"
python manage.py check
```

## Step 7: Create your first component

The [next step](./your-first-component.md) will show you how to create your first ReactPy component.

Prefer a quick summary? Read the **At a Glance** section below.

!!! info "At a Glance: Your First Component"

    <font size="5">**`my_app/components.py`**</font>

    {% include-markdown "../../../README.md" start="<!--py-header-start-->" end="<!--py-code-end-->" %}

    ---

    <font size="5">**`my_app/templates/my-template.html`**</font>

    {% include-markdown "../../../README.md" start="<!--html-header-start-->" end="<!--html-code-end-->" %}