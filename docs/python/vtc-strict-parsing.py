from django.http import HttpResponse
from reactpy import component, html

from reactpy_django.components import view_to_component


@view_to_component(strict_parsing=False)
def hello_world_view(request):
    return HttpResponse("<my-tag> Hello World </my-tag>")


@component
def my_component():
    return html.div(
        hello_world_view(),
    )
