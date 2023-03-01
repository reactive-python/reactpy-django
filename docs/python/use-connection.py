from django_reactpy.hooks import use_connection
from reactpy import component, html


@component
def my_component():
    my_connection = use_connection()
    return html.div(str(my_connection))
