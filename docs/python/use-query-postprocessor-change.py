from django_reactpy.hooks import use_query
from django_reactpy.types import QueryOptions
from reactpy import component


def my_postprocessor(data, example_kwarg=True):
    if example_kwarg:
        return data

    return dict(data)


def execute_io_intensive_operation():
    """This is an example query function that does something IO intensive."""
    pass


@component
def todo_list():
    query = use_query(
        QueryOptions(
            postprocessor=my_postprocessor,
            postprocessor_kwargs={"example_kwarg": False},
        ),
        execute_io_intensive_operation,
    )

    if query.loading or query.error:
        return None

    return str(query.data)
