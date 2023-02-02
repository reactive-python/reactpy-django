## Overview

!!! summary

    Utility functions that you can use when needed.

---

## Django Query Postprocessor

This is the default postprocessor for the `use_query` hook.

This postprocessor is designed to prevent Django's `SynchronousOnlyException` by recursively fetching all fields within a `Model` or `QuerySet` to prevent [lazy execution](https://docs.djangoproject.com/en/dev/topics/db/queries/#querysets-are-lazy).

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
