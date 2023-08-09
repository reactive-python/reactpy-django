from django.http import HttpResponse
from reactpy import component, html
from reactpy_django.components import view_to_component


@view_to_component
def hello_world_view(request, arg1, arg2, key1=None, key2=None):
    return HttpResponse(f"Hello World! {arg1} {arg2} {key1} {key2}")


@component
def my_component():
    return html.div(
        hello_world_view(
            None,  # Your request object (optional)
            "value_1",
            "value_2",
            key1="abc",
            key2="123",
        ),
    )
