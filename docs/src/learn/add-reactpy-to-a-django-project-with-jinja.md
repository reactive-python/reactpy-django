## Overview

<p class="intro" markdown>

If you use **Jinja2 templates** in your Django project and want to add ReactPy interactivity, this guide walks you through the additional configuration needed. First complete the [standard setup](./add-reactpy-to-a-django-project.md), then follow the steps below.

</p>

!!! abstract "Note"

    These docs assume you have already completed the [standard ReactPy-Django setup](./add-reactpy-to-a-django-project.md) and have a working **Django project** with Jinja2 configured.

---

## Step 1: Install `jinja2`

Jinja2 is a Python dependency you must install in your environment to use this feature.

```bash linenums="0"
pip install jinja2
```

---

## Step 2: Configure the Jinja2 template engine

Add a Jinja2 backend entry to your `TEMPLATES` list in [`settings.py`](https://docs.djangoproject.com/en/stable/topics/settings/).

The backend must include:

- `"BACKEND": "django.template.backends.jinja2.Jinja2"`
- An `"environment"` option pointing to a function that registers the `ReactPyExtension`

=== "settings.py"

    ```python
    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
        {
            "BACKEND": "django.template.backends.jinja2.Jinja2",
            "DIRS": [],
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

---

## Step 3: Create a Jinja2 environment module

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

---

## Step 4: Use ReactPy components in Jinja2 templates

With the extension registered, you can call ReactPy functions directly inside any Jinja2 template:

=== "templates/example.html.jinja"

    ```html
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

!!! info "Template tag vs Jinja2 function syntax"

    Unlike Django templates which require `{% load reactpy %}` and `{% component "..." %}`, Jinja2 allows you to call component functions directly using the `{{ component(...) }}` syntax. The registered functions are:

    | Function | Description |
    |---|---|---|
    | `{{ component(dotted_path, *args, **kwargs) }}` | Render a server-side ReactPy component. Equivalent to `{% component %}`. |
    | `{{ pyscript_component(*file_paths, initial, root) }}` | Render a client-side PyScript component. Equivalent to `{% pyscript_component %}`. |
    | `{{ pyscript_setup(*extra_py, extra_js, config) }}` | Render PyScript setup configuration. Equivalent to `{% pyscript_setup %}`. |

---

## Step 5: Verify your configuration

Run Django's [`check` command](https://docs.djangoproject.com/en/stable/ref/django-admin/#check) to verify everything is set up correctly.

```bash linenums="0"
python manage.py check
```

---

## Next steps

Now you're ready to [create your first component](./your-first-component.md).
