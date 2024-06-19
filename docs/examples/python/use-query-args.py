from reactpy import component
from reactpy_django.hooks import use_query


def example_query(value: int, other_value: bool = False): ...


@component
def my_component():
    query = use_query(example_query, {"value": 123, "other_value": True})

    return str(query.data)
