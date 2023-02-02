from django.http import HttpResponse
from idom import component, html

from django_idom.components import view_to_component


def example_transform(vdom):
    attributes = vdom.get("attributes")
    if attributes and attributes.get("id") == "hello-world":
        vdom["children"][0] = "Good Bye World!"


@view_to_component(transforms=[example_transform])
def hello_world_view(request):
    return HttpResponse("<div id='hello-world'> Hello World! <div>")


@component
def my_component():
    return html.div(
        hello_world_view(),
    )
