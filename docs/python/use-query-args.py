from django_reactpy.hooks import use_query
from reactpy import component


def example_query(value: int, other_value: bool = False):
    ...


@component
def my_component():
    query = use_query(
        example_query,
        123,
        other_value=True,
    )

    return str(query.data)
