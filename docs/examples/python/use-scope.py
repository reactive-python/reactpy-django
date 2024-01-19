from reactpy import component, html
from reactpy_django.hooks import use_scope


@component
def my_component():
    scope = use_scope()

    return html.div(str(scope))
