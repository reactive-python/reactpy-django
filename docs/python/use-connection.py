from idom import component, html

from django_idom.hooks import use_connection


@component
def my_component():
    my_connection = use_connection()
    return html.div(str(my_connection))
