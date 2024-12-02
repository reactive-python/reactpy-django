from reactpy import component, html

from example import views
from reactpy_django.components import view_to_component

hello_world_component = view_to_component(views.hello_world)


@component
def my_component():
    return html.div(
        hello_world_component(),
    )
