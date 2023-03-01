from django.http import HttpRequest, HttpResponse
from django_reactpy.components import view_to_component
from reactpy import component, html


example_request = HttpRequest()
example_request.method = "PUT"


@view_to_component
def hello_world_view(request):
    return HttpResponse(f"Hello World! {request.method}")


@component
def my_component():
    return html.div(
        hello_world_view(
            example_request,
        ),
    )
