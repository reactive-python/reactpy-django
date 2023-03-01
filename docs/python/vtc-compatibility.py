from django.http import HttpResponse
from django_reactpy.components import view_to_component
from reactpy import component, html


@view_to_component(compatibility=True)
def hello_world_view(request):
    return HttpResponse("Hello World!")


@component
def my_component():
    return html.div(
        hello_world_view(),
    )
