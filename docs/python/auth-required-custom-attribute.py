from reactpy import component, html
from reactpy_django.decorators import auth_required


@component
@auth_required(auth_attribute="is_really_cool")
def my_component():
    return html.div("I am logged in!")
