from reactpy import component, html

from example import views
from reactpy_django.components import view_to_iframe

hello_world_iframe = view_to_iframe(views.hello_world, extra_props={"title": "Hello World!"})


@component
def my_component():
    return html.div(
        hello_world_iframe(),
    )
