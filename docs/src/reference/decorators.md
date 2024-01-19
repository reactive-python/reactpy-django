## Overview

<p class="intro" markdown>

Decorator functions can be used within your `components.py` to help simplify development.

</p>

---

## User Passes Test

You can limit component access to users that pass a test function by using this decorator.

This decorator is inspired by Django's [`user_passes_test`](http://docs.djangoproject.com/en/dev/topics/auth/default/#django.contrib.auth.decorators.user_passes_test) decorator, but works with ReactPy components.

=== "components.py"

    ```python
    {% include "../../python/user-passes-test.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python test_func` | `#!python Callable[[AbstractUser], bool]` | A function that accepts a `User` returns a boolean. | N/A |
    | `#!python fallback` | `#!python Any | None` | The content to be rendered if the test fails. Typically is a ReactPy component or VDOM (`reactpy.html` snippet). |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python ComponentConstructor` | A ReactPy component constructor. |

??? question "How do I render a different component if the test fails?"

    You can use a component with the `#!python fallback` argument, as seen below.

    === "components.py"

        ```python
        {% include "../../python/user-passes-test-component-fallback.py" %}
        ```

??? question "How do I render a simple `#!python reactpy.html` snippet if the test fails?"

    You can use a `#!python reactpy.html` snippet with the `#!python fallback` argument, as seen below.

    === "components.py"

        ```python
        {% include "../../python/user-passes-test-vdom-fallback.py" %}
        ```
