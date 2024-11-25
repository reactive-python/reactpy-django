## Overview

<p class="intro" markdown>

A Single Page Application URL router, which is a variant of [`reactpy-router`](https://github.com/reactive-python/reactpy-router) that uses Django conventions.

</p>

!!! abstract "Note"

    Looking for more details on URL routing?

    This package only contains Django specific URL routing features. Standard features can be found within [`reactive-python/reactpy-router`](https://reactive-python.github.io/reactpy-router/).

---

## Django Router

URL router that enables the ability to conditionally render other components based on the client's current URL `#!python path`.

!!! warning "Pitfall"

    All pages where `#!python django_router` is used must have identical, or more permissive URL exposure within Django's [URL patterns](https://docs.djangoproject.com/en/5.0/topics/http/urls/#example). You can think of the router component as a secondary, client-side router. Django will always handle the initial load of the webpage.

    You can duplicate all your URL patterns within both Django and ReactPy, but it's easiest to use a wildcard `.*` within Django's `#!python urlpatterns` and let ReactPy handle the rest. For example...

    ```python linenums="0"
    urlpatterns = [
        re_path(r"^.*$", my_reactpy_router_view),
    ]
    ```

=== "components.py"

    ```python
    {% include "../../examples/python/django-router.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python *routes` | `#!python Route` | An object from `reactpy-router` containing a `#!python path`, `#!python element`, and child `#!python *routes`. | N/A |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python VdomDict | None` | The matched component/path after it has been fully rendered. |

??? question "How is this different from `#!python reactpy_router.browser_router`?"

    The `django_router` component utilizes the same internals as `browser_router`, but provides a more Django-like URL routing syntax.
