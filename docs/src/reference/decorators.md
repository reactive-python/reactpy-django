## Overview

<p class="intro" markdown>

Decorator functions can be used within your `components.py` to help simplify development.

</p>

---

## Auth Required

You can limit component access to users with a specific `#!python auth_attribute` by using this decorator (with or without parentheses).

By default, this decorator checks if the user is logged in and not deactivated (`#!python is_active`).

This decorator is commonly used to selectively render a component only if a user [`#!python is_staff`](https://docs.djangoproject.com/en/dev/ref/contrib/auth/#django.contrib.auth.models.User.is_staff) or [`#!python is_superuser`](https://docs.djangoproject.com/en/dev/ref/contrib/auth/#django.contrib.auth.models.User.is_superuser).

=== "components.py"

    ```python
    {% include "../../python/auth-required.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python auth_attribute` | `#!python str` | The value to check within the user object. This is checked via `#!python getattr(scope["user"], auth_attribute)`. | `#!python "is_active"` |
    | `#!python fallback` | `#!python ComponentType | VdomDict | None` | The `#!python component` or `#!python reactpy.html` snippet to render if the user is not authenticated. | `#!python None` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | #!python Component` | A ReactPy component. |
    | #!python VdomDict` | A `#!python reactpy.html` snippet. |
    | #!python None` | No component render. |

??? question "How do I render a different component if authentication fails?"

    You can use a component with the `#!python fallback` argument, as seen below.

    === "components.py"

        ```python
        {% include "../../python/auth-required-component-fallback.py" %}
        ```

??? question "How do I render a simple `#!python reactpy.html` snippet if authentication fails?"

    You can use a `#!python reactpy.html` snippet with the `#!python fallback` argument, as seen below.

    === "components.py"

        ```python
        {% include "../../python/auth-required-vdom-fallback.py" %}
        ```

??? question "How can I check if a user `#!python is_staff`?"

    You can do this by setting `#!python auth_attribute="is_staff"`, as seen blow.

    === "components.py"

        ```python
        {% include "../../python/auth-required-attribute.py" %}
        ```

??? question "How can I check for a custom attribute?"

    You will need to be using a [custom user model](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#specifying-a-custom-user-model) within your Django instance.

    For example, if your user model has the field `#!python is_really_cool` ...

    === "models.py"

        ```python
        {% include "../../python/auth-required-custom-attribute-model.py" %}
        ```

    ... then you would do the following within your decorator:

    === "components.py"

        ```python
        {% include "../../python/auth-required-custom-attribute.py" %}
        ```
