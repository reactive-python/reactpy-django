from django_reactpy.hooks import use_mutation
from reactpy import component


def example_mutation(value: int, other_value: bool = False):
    ...


@component
def my_component():
    mutation = use_mutation(example_mutation)

    mutation.execute(123, other_value=True)

    ...
