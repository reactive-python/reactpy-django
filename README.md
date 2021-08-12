# Django IDOM

<a href="https://github.com/idom-team/django-idom/actions?query=workflow%3ATest">
  <img alt="Tests" src="https://github.com/idom-team/django-idom/workflows/Test/badge.svg?event=push" />
</a>
<a href="https://pypi.python.org/pypi/django-idom">
  <img alt="Version Info" src="https://img.shields.io/pypi/v/idom.svg"/>
</a>
<a href="https://github.com/idom-team/django-idom/blob/main/LICENSE">
  <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-purple.svg">
</a>

`django-idom` allows you to integrate [IDOM](https://github.com/idom-team/idom) into
Django applications. IDOM being a package for building responsive user interfaces in
pure Python which is inspired by [ReactJS](https://reactjs.org/). For more information
on IDOM refer to [its documentation](https://idom-docs.herokuapp.com).

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


# Install Django IDOM

```bash
pip install django-idom
```

# Django Integration

To integrate IDOM into your application you'll need to modify or add the following files to `your_app`:

```
your_app/
├── __init__.py
├── asgi.py
├── settings.py
├── urls.py
└── example_app/
    ├── __init__.py
    ├── idom.py
    ├── templates/
    │   └── your-template.html
    └── urls.py
```

## `asgi.py`

To start, we'll need to use [`channels`](https://channels.readthedocs.io/en/stable/) to
create a `ProtocolTypeRouter` that will become the top of our ASGI application stack.
Under the `"websocket"` protocol, we'll then add a path for IDOM's websocket consumer
using `idom_websocket_path`. If you wish to change the route where this
websocket is served from, see the available [settings](#settings.py).

```python

import os

from django.core.asgi import get_asgi_application

from django_idom import idom_websocket_path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_app.settings")

# Fetch ASGI application before importing dependencies that require ORM models.
http_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter

application = ProtocolTypeRouter(
    {
        "http": http_asgi_app,
        "websocket": URLRouter(
          # add a path for IDOM's websocket
          [idom_websocket_path()]
        ),
    }
)
```

## `settings.py`

In your settings you'll need to add `django_idom` to the
[`INSTALLED_APPS`](https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-INSTALLED_APPS)
list:

```python
INSTALLED_APPS = [
  ...,
  "django_idom",
]
```

You may configure additional options as well:

```python
# the base URL for all IDOM-releated resources
IDOM_BASE_URL: str = "_idom/"
```

## `urls.py`

You'll need to include IDOM's static web modules path using `idom_web_modules_path`.
Similarly to the `idom_websocket_path()`. If you wish to change the route where this
websocket is served from, see the available [settings](#settings.py).

```python
from django_idom import idom_web_modules_path

urlpatterns = [
    idom_web_modules_path(),
    ...
]
```

## `example_app/components.py`

This is where, by a convention similar to that of
[`views.py`](https://docs.djangoproject.com/en/3.2/topics/http/views/), you'll define
your [IDOM](https://github.com/idom-team/idom) components. Ultimately though, you should
feel free to organize your component modules you wish. The components created here will
ultimately be referenced by name in `your-template.html`. `your-template.html`.

```python
import idom

@idom.component
def Hello(name):  # component names are camelcase by convention
    return Header(f"Hello {name}!")
```

## `example_app/templates/your-template.html`

In your templates, you may inject a view of an IDOM component into your templated HTML
by using the `idom_view` template tag. This tag which requires the name of a component
to render (of the form `module_name.ComponentName`) and keyword arguments you'd like to
pass it from the template.

```python
idom_view module_name.ComponentName param_1="something" param_2="something-else"
```

In context this will look a bit like the following...

```jinja
<!-- don't forget your load statements -->
{% load static %}
{% load idom %}

<!DOCTYPE html>
<html>
  <body>
    ...
    {% idom_view "your_app.example_app.components.Hello" name="World" %}
  </body>
</html>
```

## `example_app/views.py`

You can then serve `your-template.html` from a view just
[like any other](https://docs.djangoproject.com/en/3.2/intro/tutorial03/#write-views-that-actually-do-something).

```python
from django.http import HttpResponse
from django.template import loader


def your_template(request):
    context = {}
    return HttpResponse(
      loader.get_template("your-template.html").render(context, request)
    )
```

## `example_app/urls.py`

Include your replate in the list of urlpatterns

```python
from django.urls import path
from .views import your_template  # define this view like any other HTML template

urlpatterns = [
    path("", your_template),
    ...
]
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
