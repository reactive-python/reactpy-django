from reactpy import component, html
from reactpy_django.components import view_to_iframe

from . import views


@component
def my_component():
    return html.div(
        view_to_iframe(
            views.hello_world,
            "value_1",
            "value_2",
            key1="abc",
            key2="123",
        ),
    )
