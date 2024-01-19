## Overview

<p class="intro" markdown>

Utility functions provide various miscellaneous functionality for advanced use cases.

</p>

!!! warning "Pitfall"

    Any utility functions not documented here are not considered part of the public API and may change without notice.

---

## Register Iframe

This function is used register a view as an `#!python iframe` with ReactPy.

It is mandatory to use this function alongside [`view_to_iframe`](../reference/components.md#view-to-iframe).

=== "apps.py"

    ```python
    {% include "../../python/hello_world_app_config_fbv.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python view` | `#!python Callable | View | str` | The view to register. Can be a function or class based view, or a dotted path to a view. | N/A |

    <font size="4">**Returns**</font>

    `#!python None`

??? warning "Only use this within `#!python MyAppConfig.ready()`"

    You should always call `#!python register_iframe` within a Django [`MyAppConfig.ready()` method](https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig.ready). This ensures you will retain multiprocessing compatibility, such as with ASGI web server workers.

---

## Register Component

This function is used register a root component with ReactPy.

Typically, this function is automatically called on all components contained within Django templates.

=== "apps.py"

    ```python
    {% include "../../python/register-component.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python component` | `#!python ComponentConstructor | str` | The component to register. Can be a component function or dotted path to a component. | N/A |

    <font size="4">**Returns**</font>

    `#!python None`

??? warning "Only use this within `#!python MyAppConfig.ready()`"

    You should always call `#!python register_component` within a Django [`MyAppConfig.ready()` method](https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig.ready). This ensures you will retain multiprocessing compatibility, such as with ASGI web server workers.

??? question "Do I need to use this?"

    You typically will not need to use this function.

    For security reasons, ReactPy requires all root components to be registered. However, all components contained within Django templates are automatically registered.

    This function is needed when you have configured your [`host`](../reference/template-tag.md#component) to a dedicated Django rendering application that doesn't have templates.

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
