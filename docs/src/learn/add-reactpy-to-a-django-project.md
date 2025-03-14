## Overview

<p class="intro" markdown>

If you want to add some interactivity to your existing **Django project**, you don't have to rewrite it in ReactPy. Use [ReactPy-Django](https://github.com/reactive-python/reactpy-django) to add [ReactPy](https://github.com/reactive-python/reactpy) to your existing stack, and render interactive components anywhere.

</p>

!!! abstract "Note"

    These docs assumes you have already created [a **Django project**](https://docs.djangoproject.com/en/stable/intro/tutorial01/), which involves creating and installing at least one **Django app**.

    If do not have a **Django project**, check out this [9 minute YouTube tutorial](https://www.youtube.com/watch?v=ZsJRXS_vrw0) created by _IDG TECHtalk_.

---

## Step 1: Install from PyPI

Run the following command to install [`reactpy-django`](https://pypi.org/project/reactpy-django/) in your Python environment.

```bash linenums="0"
pip install reactpy-django
```

## Step 2: Configure `settings.py`

Add `#!python "reactpy_django"` to [`INSTALLED_APPS`](https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-INSTALLED_APPS) in your [`settings.py`](https://docs.djangoproject.com/en/stable/topics/settings/) file.

=== "settings.py"

    ```python
    {% include "../../examples/python/configure_installed_apps.py" %}
    ```

??? warning "Enable ASGI and Django Channels (Required)"

    ReactPy-Django requires Django ASGI and [Django Channels](https://github.com/django/channels) WebSockets.

    If you have not enabled ASGI on your **Django project** yet, here is a summary of the [`django`](https://docs.djangoproject.com/en/stable/howto/deployment/asgi/) and [`channels`](https://channels.readthedocs.io/en/stable/installation.html) installation docs:

    1. Install `channels[daphne]`
    2. Add `#!python "daphne"` to `#!python INSTALLED_APPS`.

        ```python linenums="0"
        {% include "../../examples/python/configure_channels_installed_app.py" %}
        ```

    3. Set your `#!python ASGI_APPLICATION` variable.

        ```python linenums="0"
        {% include "../../examples/python/configure_channels_asgi_app.py" %}
        ```

??? info "Configure ReactPy settings (Optional)"

    ReactPy's has additional configuration available to fit a variety of use cases.

    See the [ReactPy settings](../reference/settings.md) documentation to learn more.

## Step 3: Configure `urls.py`

Add ReactPy HTTP paths to your `#!python urlpatterns` in your [`urls.py`](https://docs.djangoproject.com/en/stable/topics/http/urls/) file.

=== "urls.py"

    ```python
    {% include "../../examples/python/configure_urls.py" %}
    ```

## Step 4: Configure `asgi.py`

Register ReactPy's WebSocket using `#!python REACTPY_WEBSOCKET_ROUTE` in your [`asgi.py`](https://docs.djangoproject.com/en/stable/howto/deployment/asgi/) file.

=== "asgi.py"

    ```python
    {% include "../../examples/python/configure_asgi.py" %}
    ```

??? info "Add `#!python AuthMiddlewareStack` (Optional)"

    There are many situations where you need to access the Django `#!python User` or `#!python Session` objects within ReactPy components. For example, if you want to:

    1. Access the `#!python User` that is currently logged in
    3. Access Django's `#!python Session` object
    2. Login or logout the current `#!python User`

    In these situations will need to ensure you are using `#!python AuthMiddlewareStack`.

    {% include "../../includes/auth-middleware-stack.md" %}

??? question "Where is my `asgi.py`?"

    If you do not have an `asgi.py`, follow the [`channels` installation guide](https://channels.readthedocs.io/en/stable/installation.html).

## Step 5: Run database migrations

Run Django's [`migrate` command](https://docs.djangoproject.com/en/stable/topics/migrations/) to initialize ReactPy-Django's database table.

```bash linenums="0"
python manage.py migrate
```

## Step 6: Check your configuration

Run Django's [`check` command](https://docs.djangoproject.com/en/stable/ref/django-admin/#check) to verify if ReactPy was set up correctly.

```bash linenums="0"
python manage.py check
```

## Step 7: Create your first component

The [next page](./your-first-component.md) will show you how to create your first ReactPy component.

Prefer a quick summary? Read the **At a Glance** section below.

!!! info "At a Glance"

    <font size="5">**`my_app/components.py`**</font>

    {% include-markdown "../../../README.md" start="<!--py-header-start-->" end="<!--py-code-end-->" %}

    ---

    <font size="5">**`my_app/templates/my_template.html`**</font>

    {% include-markdown "../../../README.md" start="<!--html-header-start-->" end="<!--html-code-end-->" %}
