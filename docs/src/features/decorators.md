## Overview

!!! summary

    Decorator utilities can be used within your `components.py` to help simplify development.

---

## Auth Required

You can limit access to a component to users with a specific `auth_attribute` by using this decorator (with or without parentheses).

By default, this decorator checks if the user is logged in, and his/her account has not been deactivated.

This decorator is commonly used to selectively render a component only if a user [`is_staff`](https://docs.djangoproject.com/en/dev/ref/contrib/auth/#django.contrib.auth.models.User.is_staff) or [`is_superuser`](https://docs.djangoproject.com/en/dev/ref/contrib/auth/#django.contrib.auth.models.User.is_superuser).

=== "components.py"

    ```python
    {% include "../../python/auth-required.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `auth_attribute` | `str` | The value to check within the user object. This is checked in the form of `UserModel.<auth_attribute>`. | `#!python "is_active"` |
    | `fallback` | `ComponentType`, `VdomDict`, `None` | The `component` or `reactpy.html` snippet to render if the user is not authenticated. | `None` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `Component` | An ReactPy component. |
    | `VdomDict` | An `reactpy.html` snippet. |
    | `None` | No component render. |

??? question "How do I render a different component if authentication fails?"

    You can use a component with the `fallback` argument, as seen below.

    === "components.py"

        ```python
        {% include "../../python/auth-required-component-fallback.py" %}
        ```

??? question "How do I render a simple `reactpy.html` snippet if authentication fails?"

    You can use a `reactpy.html` snippet with the `fallback` argument, as seen below.

    === "components.py"

        ```python
        {% include "../../python/auth-required-vdom-fallback.py" %}
        ```

??? question "How can I check if a user `is_staff`?"

    You can set the `auth_attribute` to `is_staff`, as seen blow.

    === "components.py"

        ```python
        {% include "../../python/auth-required-attribute.py" %}
        ```

??? question "How can I check for a custom attribute?"

    You will need to be using a [custom user model](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#specifying-a-custom-user-model) within your Django instance.

    For example, if your user model has the field `is_really_cool` ...

    === "models.py"

        ```python
        {% include "../../python/auth-required-custom-attribute-model.py" %}
        ```

    ... then you would do the following within your decorator:

    === "components.py"

        ```python
        {% include "../../python/auth-required-custom-attribute.py" %}
        ```
