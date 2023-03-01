from django_reactpy.hooks import use_location
from reactpy import component, html


@component
def my_component():
    my_location = use_location()
    return html.div(str(my_location))
