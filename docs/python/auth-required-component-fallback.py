from idom import component, html

from django_idom.decorators import auth_required


@component
def my_component_fallback():
    return html.div("I am NOT logged in!")


@component
@auth_required(fallback=my_component_fallback)
def my_component():
    return html.div("I am logged in!")
