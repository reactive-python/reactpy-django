from idom import component, html

from django_idom.decorators import auth_required


@component
@auth_required(fallback=html.div("I am NOT logged in!"))
def my_component():
    return html.div("I am logged in!")
