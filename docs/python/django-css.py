from reactpy import component, html
from reactpy_django.components import django_css


@component
def my_component():
    return html.div(
        django_css("css/buttons.css"),
        html.button("My Button!"),
    )
