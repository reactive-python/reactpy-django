from reactpy import component, html
from reactpy_django.components import view_to_component

from . import views

hello_world_component = view_to_component(views.hello_world)


@component
def my_component():
    return html.div(
        hello_world_component(),
    )
