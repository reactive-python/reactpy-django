from reactpy import component, html
from reactpy_django.hooks import use_location


@component
def my_component():
    location = use_location()

    return html.div(location.pathname + location.search)
