from idom import component

from django_idom.hooks import use_query
from django_idom.types import QueryOptions


def execute_io_intensive_operation():
    """This is an example query function that does something IO intensive."""
    pass


@component
def todo_list():
    query = use_query(
        QueryOptions(postprocessor=None),
        execute_io_intensive_operation,
    )

    if query.loading or query.error:
        return None

    return str(query.data)
