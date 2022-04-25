???+ summary

    Select your template containing an IDOM component, and render it using a Django view.

---

We will assume you've [created a Django View](https://docs.djangoproject.com/en/dev/intro/tutorial01/#write-your-first-view) before, but we'll give a simple example below.

Within your **Django app**'s [`views.py` file](https://docs.djangoproject.com/en/dev/intro/tutorial01/#write-your-first-view), you'll need to create a function to render the HTML template containing your IDOM components.

```python title="views.py"
from django.shortcuts import render

def index(request):
    return render(request, "my-template.html")
```

To simplify things for this example, we will add this new view directly to your [**Django project**'s `urls.py`](https://docs.djangoproject.com/en/dev/intro/tutorial01/#write-your-first-view) rather than adding to a **Django app**'s `urls.py`.

```python title="urls.py"
from django.urls import path
from example_project.my_app import views

urlpatterns = [
    path("example/", views.index),
]
```

Now, navigate to `http://127.0.0.1:8000/example/`. If you copy-pasted the component from the previous example, you will now see your component display "Hello World".
