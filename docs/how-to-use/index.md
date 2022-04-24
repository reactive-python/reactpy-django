## Create a Django project and app

We are going to assume you've [created a basic **Django project**](https://docs.djangoproject.com/en/dev/intro/tutorial01/) before, which also involves creating/installing at least one **Django app**. If not, check out this [9 minute video tutorial](https://www.youtube.com/watch?v=ZsJRXS_vrw0) created by _IDG TECHtalk_.

Django provides you the flexibility to place your apps anywhere you wish. In the examples below, we are going to assume you've placed your apps directly into your **Django project** folder. This is a common folder structure for small projects.

---

## Create a component

### `components.py`

{%
   include-markdown "../../README.md"
   start="<!--py-example-start-->"
   end="<!--py-example-end-->"
%}

---

## Reference your component

### `templates/my-template.html`

{%
   include-markdown "../../README.md"
   start="<!--html-example-start-->"
   end="<!--html-example-end-->"
%}

---

## Render your component

We will also assume you've [created a Django View](https://docs.djangoproject.com/en/dev/intro/tutorial01/#write-your-first-view) before, but we'll give a simple example below.

### `views.py`

This is your **Django app**'s [view file](https://docs.djangoproject.com/en/dev/intro/tutorial01/#write-your-first-view). This function will render your HTML template, which includes your IDOM component.

```python
from django.shortcuts import render

def index(request):
    return render(request, "my-template.html")
```

### `urls.py`

To simplify things for this example, we are adding this view directly to your [**Django project**'s `urls.py`](https://docs.djangoproject.com/en/dev/intro/tutorial01/#write-your-first-view) rather than adding to a **Django app**.

```python
from django.urls import path
from . import views

urlpatterns = [
    path("example/", views.index),
]
```

Now, navigate to `http://127.0.0.1:8000/example/` to see your component print out "Hello World".
