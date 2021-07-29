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
├── asgi.py
├── components.py
├── idom.py
├── settings.py
├── templates/
│   ├── your-template.html
└── urls.py
```

## `asgi.py`

To start, we'll need to use [`channels`](https://channels.readthedocs.io/en/stable/) to
create a `ProtocolTypeRouter` that will become the top of our ASGI application stack.
Under the `"websocket"` protocol, we'll then add a path for IDOM's websocket consumer
using `django_idom_websocket_consumer_path`. If you wish to change the route where this
websocket is served from see the [settings](#configuration-options).

```python

import os

from django.core.asgi import get_asgi_application

from django_idom import django_idom_websocket_consumer_path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_app.settings")

# Fetch ASGI application before importing dependencies that require ORM models.
http_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter

application = ProtocolTypeRouter(
    {
        "http": http_asgi_app,
        "websocket": URLRouter(
          # add a path for IDOM's websocket
          [django_idom_websocket_consumer_path()]
        ),
    }
)
```

## `components.py`

This is where, by a convention similar to that of
[`views.py`](https://docs.djangoproject.com/en/3.2/topics/http/views/), you'll define
your [IDOM](https://github.com/idom-team/idom) components. Ultimately though, you should
feel free to organize your component modules you wish.

```python
import idom

@idom.component
def Hello(name):  # component names are camelcase by convention
    return idom.html.h1(f"Hello {name}!")
```

## `idom.py`

This file is automatically discovered by `django-idom` when scanning the list of
[`INSTALLED_APPS`](https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-INSTALLED_APPS).
All apps that export components will contain this module.

Inside this module must be a `components` list that is imported from
[`components.py`](#components.py):

```python
from .components import Hello

components = [Hello]
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

## `templates/your-template.html`

In your templates, you may inject a view of an IDOM component into your templated HTML
by using the `idom_view` Jinja tag. This tag which requires the name of a component to
render (of the form `app_name.ComponentName`) and keyword arguments you'd like to pass
it from the template.

```python
idom_view app_name.ComponentName param_1="something" param_2="something-else"
```

In context this will look a bit like the following...

```html
<!-- don't forget your load statements -->
{% load static %}
{% load idom %}

<!DOCTYPE html>
<html>
  <body>
    ...
    {% idom_view "test_app.Hello" name="World" %}
  </body>
</html>
```

Your view for this template can be defined just
[like any other](https://docs.djangoproject.com/en/3.2/intro/tutorial03/#write-views-that-actually-do-something).

## `urls.py`

To your list of URLs you'll need to include IDOM's static web modules path using
`django_idom_web_modules_path`:

```python
from django.urls import path
from django_idom import django_idom_web_modules_path
from .views import your_template  # define this view like any other HTML template


urlpatterns = [
    path("", your_template),
    django_idom_web_modules_path(),
]
```

# Configuration Options

You may configure additional options in your `settings.py` file

```python
# the base URL for all IDOM-releated resources
IDOM_BASE_URL: str = "_idom/"

# ignore these INSTALLED_APPS during component collection
IDOM_IGNORE_INSTALLED_APPS: set[str] = {"some_app", "some_other_app"}
```
