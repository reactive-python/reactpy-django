## Overview

<p class="intro" markdown>

A variant of [`reactpy-router`](https://github.com/reactive-python/reactpy-router) that utilizes Django conventions.

</p>

!!! abstract "Note"

    Looking for more details on URL routing?

    This package only contains Django specific URL routing features. Standard features can be found within [`reactive-python/reactpy-router`](https://reactive-python.github.io/reactpy-router/).

---

## Django Router

URL router that enables the ability to conditionally render other components based on the client's current URL `#!python path`.

=== "components.py"

    ```python
    {% include "../../python/django-router.py" %}
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

??? question "How is this different from `#!python reactpy_router.simple.router`?"

    This component utilizes `reactpy-router` under the hood, but provides a more Django-like URL routing syntax.
