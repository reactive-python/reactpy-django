from django_reactpy.decorators import auth_required
from reactpy import component, html


@component
def my_component_fallback():
    return html.div("I am NOT logged in!")


@component
@auth_required(fallback=my_component_fallback)
def my_component():
    return html.div("I am logged in!")
