from django_reactpy.hooks import use_query
from django_reactpy.types import QueryOptions
from django_reactpy.utils import django_query_postprocessor
from example.models import TodoItem
from reactpy import component


def get_items():
    return TodoItem.objects.all()


@component
def todo_list():
    # These `QueryOptions` are functionally equivalent to Django-ReactPy's default values
    item_query = use_query(
        QueryOptions(
            postprocessor=django_query_postprocessor,
            postprocessor_kwargs={"many_to_many": True, "many_to_one": True},
        ),
        get_items,
    )

    return item_query.data
