# Django IDOM &middot; [![Tests](https://github.com/idom-team/django-idom/workflows/Test/badge.svg?event=push)](https://github.com/idom-team/django-idom/actions?query=workflow%3ATest) [![PyPI Version](https://img.shields.io/pypi/v/django-idom.svg)](https://pypi.python.org/pypi/django-idom) [![License](https://img.shields.io/badge/License-MIT-purple.svg)](https://github.com/idom-team/django-idom/blob/main/LICENSE)

`django-idom` allows Django to integrate with [IDOM](https://github.com/idom-team/idom), a reactive Python web framework for building **interactive websites without needing a single line of Javascript**.

**You can try IDOM now in a Jupyter Notebook:**
<a
  target="_blank"
  href="https://mybinder.org/v2/gh/idom-team/idom-jupyter/main?filepath=notebooks%2Fintroduction.ipynb">
<img
    alt="Binder"
    valign="bottom"
    height="21px"
    src="https://mybinder.org/badge_logo.svg"/>
</a>

# Quick Example

## `example_app/components.py`

This is where you'll define your [IDOM](https://github.com/idom-team/idom) components. Ultimately though, you should
feel free to organize your component modules as you wish. Any components created will ultimately be referenced
by Python dotted path in `your-template.html`.

```python
from idom import component, html
from django_idom import IdomWebsocket

# Components are CamelCase by ReactJS convention
@component
def Hello(websocket: IdomWebsocket, greeting_recipient: str):
    return html.h1(f"Hello {greeting_recipient}!")
```

## [`example_app/templates/your-template.html`](https://docs.djangoproject.com/en/dev/topics/templates/)

In your templates, you may add IDOM components into your HTML by using the `idom_component`
template tag. This tag requires the dotted path to the component function.

Additonally, you can pass in keyworded arguments into your component function.

In context this will look a bit like the following...

```jinja
{% load idom %}

<!DOCTYPE html>
<html>
  <head>
    <title>Example Project</title>
  </head>

  <body>
    {% idom_component "my_django_project.example_app.components.Hello" greeting_recipient="World" %}
  </body>
</html>
```

# Installation

Install `django-idom` via pip.

```bash
pip install django-idom
```

You'll also need to modify a few files in your Django project.

## [`settings.py`](https://docs.djangoproject.com/en/dev/topics/settings/)

In your settings you'll need to add `channels` and `django_idom` to [`INSTALLED_APPS`](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-INSTALLED_APPS).

```python
INSTALLED_APPS = [
  ...,
  "channels",
  "django_idom",
]

# Ensure ASGI_APPLICATION is set properly based on your project name!
ASGI_APPLICATION = "my_django_project.asgi.application"
```

**Optional:** You can also configure IDOM settings.

```python
# If "idom" cache is not configured, then we'll use "default" instead
CACHES = {
  "idom": {"BACKEND": ...},
}

# Maximum seconds between two reconnection attempts that would cause the client give up.
# 0 will disable reconnection.
IDOM_WS_MAX_RECONNECT_TIMEOUT: int = 604800

# The URL for IDOM to serve websockets
IDOM_WEBSOCKET_URL: str = "idom/"
```

## [`urls.py`](https://docs.djangoproject.com/en/dev/topics/http/urls/)

Add IDOM HTTP paths to your `urlpatterns`.

```python
from django.urls import include, path

urlpatterns = [
    path("idom/", include("django_idom.http.urls")),
    ...
]
```

## [`asgi.py`](https://docs.djangoproject.com/en/dev/howto/deployment/asgi/)

Register IDOM's websocket using `IDOM_WEBSOCKET_PATH`.

_Note: If you do not have an `asgi.py`, follow the [`channels` installation guide](https://channels.readthedocs.io/en/stable/installation.html)._

```python

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

# Developer Guide

If you plan to make code changes to this repository, you'll need to install the
following dependencies first:

- [NPM](https://docs.npmjs.com/try-the-latest-stable-version-of-npm) for
  installing and managing Javascript
- [ChromeDriver](https://chromedriver.chromium.org/downloads) for testing with
  [Selenium](https://www.seleniumhq.org/)

Once done, you should clone this repository:

```bash
git clone https://github.com/idom-team/django-idom.git
cd django-idom
```

Then, by running the command below you can:

- Install an editable version of the Python code

- Download, build, and install Javascript dependencies

```bash
pip install -e . -r requirements.txt
```

Finally, to verify that everything is working properly, you'll want to run the test suite.

## Running The Tests

This repo uses [Nox](https://nox.thea.codes/en/stable/) to run scripts which can
be found in `noxfile.py`. For a full test of available scripts run `nox -l`. To run the full test suite simple execute:

```
nox -s test
```

To run the tests using a headless browser:

```
nox -s test -- --headless
```
