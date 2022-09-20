???+ summary

    Select your template containing an IDOM component, and render it using a Django view.

---

We will assume you've [created a Django View](https://docs.djangoproject.com/en/dev/intro/tutorial01/#write-your-first-view) before, but here's a simple example below.

Within your **Django app**'s `views.py` file, you'll need to create a function to render the HTML template containing your IDOM components.

In this example, we will create a view that renders `my-template.html` (_from the previous step_).

```python title="views.py"
from django.shortcuts import render

def index(request):
    return render(request, "my-template.html")
```

We will add this new view into your [`urls.py`](https://docs.djangoproject.com/en/dev/intro/tutorial01/#write-your-first-view).

```python title="urls.py"
from django.urls import path
from example_project.my_app import views

urlpatterns = [
    path("example/", views.index),
]
```

Now, navigate to `http://127.0.0.1:8000/example/`. If you copy-pasted the component from the previous example, you will now see your component display "Hello World".

??? question "Which urls.py do I add my views to?"

    For simple **Django projects**, you can easily add all of your views directly into the **Django project's** `urls.py`. However, as you start increase your project's complexity you might end up with way too much within one file.

    Once you reach that point, we recommend creating an individual `urls.py` within each of your **Django apps**.

    Then, within your **Django project's** `urls.py` you will use Django's [`include` function](https://docs.djangoproject.com/en/dev/ref/urls/#include) to link it all together.
