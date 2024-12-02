from reactpy import component, html

from reactpy_django.components import django_js


@component
def my_component():
    return html.div(
        html.button("My Button!"),
        django_js("js/scripts.js"),
    )
