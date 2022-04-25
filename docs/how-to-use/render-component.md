## Reference your component

### `templates/my-template.html`

{% include-markdown "../../README.md" start="<!--html-header-start-->" end="<!--html-header-end-->" %}

{% include-markdown "../../README.md" start="<!--html-code-start-->" end="<!--html-code-end-->" %}

!!! note "Note: Django HTML Templates"

        If you do not have a `templates` folder in your **Django app**, simply create one! Keep in mind, templates within this folder will not be detected unless you [add the corresponding **Django app** to `settings.py:INSTALLED_APPS`](https://docs.djangoproject.com/en/dev/ref/applications/#configuring-applications).

!!! note "Note: `recipient` Argument"

        Pay attention to how the function definition for HelloComponent (_in the previous example_) accepts a 'recipient' arguement.

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

To simplify things for this example, we are adding this view directly to your [**Django project**'s `urls.py`](https://docs.djangoproject.com/en/dev/intro/tutorial01/#write-your-first-view) rather than adding to a **Django app**'s `urls.py`.

```python
from django.urls import path
from . import views

urlpatterns = [
    path("example/", views.index),
]
```

Now, navigate to `http://127.0.0.1:8000/example/` to see your component print out "Hello World".
