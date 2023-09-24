from reactpy import component, html
from reactpy_django.components import view_to_iframe

from . import views

hello_world_iframe = view_to_iframe(views.HelloWorld.as_view())


@component
def my_component():
    return html.div(
        hello_world_iframe(),
    )
