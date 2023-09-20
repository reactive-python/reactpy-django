## Overview

<p class="intro" markdown>

Utility functions provide various miscellaneous functionality. These are typically not used, but are available for advanced use cases.

</p>

---

## Django Query Postprocessor

This is the default postprocessor for the `#!python use_query` hook.

This postprocessor is designed to avoid Django's `#!python SynchronousOnlyException` by recursively fetching all fields within a `#!python Model` or `#!python QuerySet` to prevent [lazy execution](https://docs.djangoproject.com/en/dev/topics/db/queries/#querysets-are-lazy).

=== "components.py"

    ```python
    {% include "../../python/django-query-postprocessor.py" %}
    ```

=== "models.py"

    ```python
    {% include "../../python/example/models.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python data` | `#!python QuerySet | Model` | The `#!python Model` or `#!python QuerySet` to recursively fetch fields from. | N/A |
    | `#!python many_to_many` | `#!python bool` | Whether or not to recursively fetch `#!python ManyToManyField` relationships. | `#!python True` |
    | `#!python many_to_one` | `#!python bool` | Whether or not to recursively fetch `#!python ForeignKey` relationships. | `#!python True` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python QuerySet | Model` | The `#!python Model` or `#!python QuerySet` with all fields fetched. |

## Register Component

This function is used manually register a root component with ReactPy.

=== "apps.py"

    ```python
    {% include "../../python/register-component.py" %}
    ```

??? warning "Only use this within `#!python MyAppConfig.ready()`"

    You should always call `#!python register_component` within a Django [`#!python MyAppConfig.ready()` method](https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig.ready). This ensures you will retain multiprocessing compatibility, such as with ASGI web server workers.

??? question "Do I need to use this?"

    You typically will not need to use this function.

    For security reasons, ReactPy requires all root components to be registered. However, all components contained within Django templates are automatically registered.

    This function is needed when you have configured your [`host`](../reference/template-tag.md#component) to a dedicated Django rendering application that doesn't have templates.
