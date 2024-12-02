from django.http import HttpRequest
from reactpy import component, html

from example import views
from reactpy_django.components import view_to_component

hello_world_component = view_to_component(views.hello_world)


@component
def my_component():
    request = HttpRequest()
    request.method = "GET"

    return html.div(
        hello_world_component(
            request,  # This request object is optional.
            "value_1",
            "value_2",
            kwarg1="abc",
            kwarg2="123",
        ),
    )
