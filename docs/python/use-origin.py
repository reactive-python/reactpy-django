from django_reactpy.hooks import use_origin
from reactpy import component, html


@component
def my_component():
    my_origin = use_origin()
    return html.div(my_origin or "No origin")
