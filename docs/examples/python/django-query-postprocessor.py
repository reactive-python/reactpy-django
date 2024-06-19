from example.models import TodoItem
from reactpy import component
from reactpy_django.hooks import use_query
from reactpy_django.utils import django_query_postprocessor


def get_items():
    return TodoItem.objects.all()


@component
def todo_list():
    # These postprocessor options are functionally equivalent to ReactPy-Django's default values
    item_query = use_query(
        get_items,
        postprocessor=django_query_postprocessor,
        postprocessor_kwargs={"many_to_many": True, "many_to_one": True},
    )

    return item_query.data
