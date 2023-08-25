## Overview

<p class="intro" markdown>

Utility functions provide various miscellaneous functionality. These are typically not used, but are available for advanced use cases.

</p>

---

## Django Query Postprocessor

This is the default postprocessor for the `use_query` hook.

This postprocessor is designed to avoid Django's `SynchronousOnlyException` by recursively fetching all fields within a `Model` or `QuerySet` to prevent [lazy execution](https://docs.djangoproject.com/en/dev/topics/db/queries/#querysets-are-lazy).

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
    | `data` | `QuerySet | Model` | The `Model` or `QuerySet` to recursively fetch fields from. | N/A |
    | `many_to_many` | `bool` | Whether or not to recursively fetch `ManyToManyField` relationships. | `True` |
    | `many_to_one` | `bool` | Whether or not to recursively fetch `ForeignKey` relationships. | `True` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `QuerySet | Model` | The `Model` or `QuerySet` with all fields fetched. |

## Register Component

The `register_component` function is used manually register a root component with ReactPy.

You should always call `register_component` within a Django [`AppConfig.ready()` method](https://docs.djangoproject.com/en/4.2/ref/applications/#django.apps.AppConfig.ready) to retain compatibility with ASGI webserver workers.

=== "apps.py"

    ```python
    {% include "../../python/register-component.py" %}
    ```

??? question "Do I need to register my components?"

    You typically will not need to use this function.

    For security reasons, ReactPy does not allow non-registered components to be root components. However, all components contained within Django templates are automatically considered root components.

    You only need to use this function if your host application does not contain any HTML templates that [reference](../features/template-tag.md#component) your components.

    A common scenario where this is needed is when you are modifying the [template tag `host = ...` argument](../features/template-tag.md#component) in order to configure a dedicated Django application as a rendering server for ReactPy. On this dedicated rendering server, you would need to manually register your components.
