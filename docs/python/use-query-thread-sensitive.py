from reactpy import component
from reactpy_django.hooks import use_query
from reactpy_django.types import QueryOptions


def execute_thread_safe_operation():
    """This is an example query function that does some thread-safe operation."""
    pass


@component
def my_component():
    query = use_query(
        QueryOptions(thread_sensitive=False),
        execute_thread_safe_operation,
    )

    if query.loading or query.error:
        return None

    return str(query.data)
