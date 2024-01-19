from reactpy import component
from reactpy_django.hooks import use_mutation


def example_mutation(value: int, other_value: bool = False):
    ...


@component
def my_component():
    mutation = use_mutation(example_mutation)

    mutation(123, other_value=True)

    ...
