from reactpy import component, html
from reactpy_django.hooks import use_user


@component
def my_component():
    user = use_user()

    return html.div(user.username)
