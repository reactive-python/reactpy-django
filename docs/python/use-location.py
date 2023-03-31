from reactpy import component, html

from reactpy_django.hooks import use_location


@component
def my_component():
    my_location = use_location()
    return html.div(str(my_location))
