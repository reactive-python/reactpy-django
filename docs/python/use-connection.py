from reactpy import component, html
from reactpy_django.hooks import use_connection


@component
def my_component():
    connection = use_connection()

    return html.div(str(connection))
