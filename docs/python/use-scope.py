from django_reactpy.hooks import use_scope
from reactpy import component, html


@component
def my_component():
    my_scope = use_scope()
    return html.div(str(my_scope))
