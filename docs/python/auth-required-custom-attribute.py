from idom import component, html

from django_idom.decorators import auth_required


@component
@auth_required(auth_attribute="is_really_cool")
def my_component():
    return html.div("I am logged in!")
