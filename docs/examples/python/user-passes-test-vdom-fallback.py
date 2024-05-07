from reactpy import component, html
from reactpy_django.decorators import user_passes_test


def is_authenticated(user):
    return user.is_authenticated


@user_passes_test(is_authenticated, fallback=html.div("I am NOT logged in!"))
@component
def my_component():
    return html.div("I am logged in!")
