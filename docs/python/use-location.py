from reactpy import component, html
from reactpy_django.hooks import use_location


@component
def my_component():
    my_location = use_location()
    return html.div(my_location.pathname + my_location.search)
