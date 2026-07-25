## Overview

<p class="intro" markdown>

If you use **Jinja2 templates** in your Django project and want to add ReactPy interactivity, this guide walks you through the additional configuration needed. First complete the [standard setup](./add-reactpy-to-a-django-project.md), then follow the steps below.

</p>

!!! abstract "Note"

    These docs assume you have already completed the [standard ReactPy-Django setup](./add-reactpy-to-a-django-project.md) and have a working **Django project** with Jinja2 configured.

---

## Step 1: Install from PyPI

Run the following command to install [`reactpy-django`](https://pypi.org/project/reactpy-django/) and [`jinja2`](https://pypi.org/project/Jinja2/) in your Python environment.

```bash linenums="0"
pip install reactpy-django jinja2
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

Also add a Jinja2 backend entry to your `TEMPLATES` list:

The backend must include:

- `"BACKEND": "django.template.backends.jinja2.Jinja2"`
- An `"environment"` option pointing to a function that registers the `ReactPyExtension`

=== "settings.py"

    ```python
    import os

    TEMPLATES = [
        ... ,
        {
            "BACKEND": "django.template.backends.jinja2.Jinja2",
            "DIRS": [os.path.join(BASE_DIR, "templates")],
            "OPTIONS": {
                "environment": "myproject.jinja_env.environment",
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]
    ```

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

## Step 5: Register the Jinja2 Extension

Create a `jinja_env.py` module that registers the `ReactPyExtension`:

=== "myproject/jinja_env.py"

    ```python
    from jinja2 import Environment
    from reactpy_django.templatetags.jinja import ReactPyExtension


    def environment(**options):
        env = Environment(**options)
        env.add_extension(ReactPyExtension)
        return env
    ```

## Step 6: Run database migrations

Run Django's [`migrate` command](https://docs.djangoproject.com/en/stable/topics/migrations/) to initialize ReactPy-Django's database table.

```bash linenums="0"
python manage.py migrate
```

## Step 7: Check your configuration

Run Django's [`check` command](https://docs.djangoproject.com/en/stable/ref/django-admin/#check) to verify everything is set up correctly.

```bash linenums="0"
python manage.py check
```

## Step 8: Create your first component

The [next page](./your-first-component.md) will show you how to create your first ReactPy component.

Prefer a quick summary? Read the **At a Glance** section below.

!!! info "At a Glance"

    With the extension registered, you can call ReactPy functions directly inside any Jinja2 template:

    === "templates/example.jinja"

        ```jinja
        <!DOCTYPE html>
        <html>
        <head>
            <title>ReactPy + Jinja2</title>
        </head>
        <body>
            <h1>Server-side component</h1>
            {{ component("my_app.components.hello_world", recipient="World") }}

            <h1>Client-side PyScript component</h1>
            {{ pyscript_component("my_app/components/my_app.py") }}

            {{ pyscript_setup() }}
        </body>
        </html>
        ```

    ---

    <font size="5">**`my_app/components.py`**</font>

    {% include-markdown "../../../README.md" start="<!--py-header-start-->" end="<!--py-code-end-->" %}

    ---

    <font size="5">**`my_app/templates/my_template.jinja`**</font>

    In your Jinja2 template, call the `component` function directly with the dotted path to your component:

    ```jinja
    <!DOCTYPE html>
    <html>
      <body>
        {{ component("my_app.components.hello_world", recipient="World") }}
      </body>
    </html>
    ```

    ??? info "Template tag vs Jinja2 function syntax"

        Unlike Django templates which require `{% load reactpy %}` and `{% component "..." %}`, Jinja2 allows you to call component functions directly using the `{{ component(...) }}` syntax. The registered functions are:

        | Function | Description |
        |---|---|
        | `{{ component(dotted_path, *args, **kwargs) }}` | Render a server-side ReactPy component. Equivalent to `{% component ... %}`. |
        | `{{ pyscript_component(*file_paths, initial, root) }}` | Render a client-side PyScript component. Equivalent to `{% pyscript_component ... %}`. |
        | `{{ pyscript_setup(*extra_py, extra_js, config) }}` | Render PyScript setup configuration. Equivalent to `{% pyscript_setup ... %}`. |
