from reactpy import component
from reactpy_django.hooks import use_query


def my_postprocessor(data, example_kwarg=True):
    if example_kwarg:
        return data

    return dict(data)


def execute_io_intensive_operation():
    """This is an example query function that does something IO intensive."""
    pass


@component
def my_component():
    query = use_query(
        execute_io_intensive_operation,
        postprocessor=my_postprocessor,
        postprocessor_kwargs={"example_kwarg": False},
    )

    if query.loading or query.error:
        return None

    return str(query.data)
