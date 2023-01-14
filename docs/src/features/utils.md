???+ summary

    Utility functions that you can use when needed.

## Django Query Postprocessor

This is the default postprocessor for the `use_query` hook.

This postprocessor is designed to prevent Django's `SynchronousOnlyException` by recursively fetching all fields within a `Model` or `QuerySet` to prevent [lazy execution](https://docs.djangoproject.com/en/dev/topics/db/queries/#querysets-are-lazy).

=== "components.py"

    ```python
    from example_project.my_app.models import TodoItem
    from idom import component
    from django_idom.hooks import use_query
    from django_idom.types import QueryOptions
    from django_idom.utils import django_query_postprocessor

    def get_items():
        return TodoItem.objects.all()

    @component
    def todo_list():
        # These `QueryOptions` are functionally equivalent to Django-IDOM's default values
        item_query = use_query(
            QueryOptions(
                postprocessor=django_query_postprocessor,
                postprocessor_kwargs={"many_to_many": True, "many_to_one": True},
            ),
            get_items,
        )

        ...
    ```

=== "models.py"

    ```python
    from django.db import models

    class TodoItem(models.Model):
        text = models.CharField(max_length=255)
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
