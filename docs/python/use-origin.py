from reactpy import component, html
from reactpy_django.hooks import use_origin


@component
def my_component():
    origin = use_origin()

    return html.div(origin or "No origin")
