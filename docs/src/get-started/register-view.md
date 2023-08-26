## Overview

<p class="intro" markdown>

Render your template containing your ReactPy component using a Django view.

</p>

!!! Note

    We assume you have [created a Django View](https://docs.djangoproject.com/en/dev/intro/tutorial01/#write-your-first-view) before, but we have included a simple example below.

---

## Creating a Django view and URL path

Within your **Django app**'s `views.py` file, you will need to create a function to render the HTML template containing your ReactPy components.

In this example, we will create a view that renders `my-template.html` ([_from the previous step_](./use-template-tag.md)).

=== "views.py"

    ```python
    {% include "../../python/example/views.py" %}
    ```

We will add this new view into your [`urls.py`](https://docs.djangoproject.com/en/dev/intro/tutorial01/#write-your-first-view).

=== "urls.py"

    ```python
    {% include "../../python/example/urls.py" %}
    ```

??? question "Which urls.py do I add my views to?"

    For simple **Django projects**, you can easily add all of your views directly into the **Django project's** `urls.py`. However, as you start increase your project's complexity you might end up with way too much within one file.

    Once you reach that point, we recommend creating an individual `urls.py` within each of your **Django apps**.

    Then, within your **Django project's** `urls.py` you will use Django's [`include` function](https://docs.djangoproject.com/en/dev/ref/urls/#include) to link it all together.
