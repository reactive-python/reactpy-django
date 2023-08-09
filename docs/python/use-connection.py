from reactpy import component, html
from reactpy_django.hooks import use_connection


@component
def my_component():
    my_connection = use_connection()
    return html.div(str(my_connection))
