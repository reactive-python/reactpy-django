from reactpy import component, html
from reactpy_django.components import view_to_component

from . import views


def example_transform(vdom):
    attributes = vdom.get("attributes")
    if attributes and attributes.get("id") == "hello-world":
        vdom["children"][0] = "Farewell World!"


hello_world_component = view_to_component(
    views.hello_world, transforms=[example_transform]
)


@component
def my_component():
    return html.div(
        hello_world_component(),
    )
