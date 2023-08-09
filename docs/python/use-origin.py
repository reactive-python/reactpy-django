from reactpy import component, html
from reactpy_django.hooks import use_origin


@component
def my_component():
    my_origin = use_origin()
    return html.div(my_origin or "No origin")
