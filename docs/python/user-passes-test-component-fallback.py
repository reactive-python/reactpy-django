from reactpy import component, html
from reactpy_django.decorators import user_passes_test


@component
def my_component_fallback():
    return html.div("I am NOT logged in!")


def auth_check(user):
    return user.is_authenticated


@user_passes_test(auth_check, fallback=my_component_fallback)
@component
def my_component():
    return html.div("I am logged in!")
