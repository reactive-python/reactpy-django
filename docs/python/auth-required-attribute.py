from reactpy import component, html

from django_reactpy.decorators import auth_required


@component
@auth_required(auth_attribute="is_staff")
def my_component():
    return html.div("I am logged in!")
