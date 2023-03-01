from django_reactpy.components import django_js
from reactpy import component, html


@component
def my_component():
    return html.div(
        html.button("My Button!"),
        django_js("js/scripts.js"),
    )
