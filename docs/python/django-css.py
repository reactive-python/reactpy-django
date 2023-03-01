from django_reactpy.components import django_css
from reactpy import component, html


@component
def my_component():
    return html.div(
        django_css("css/buttons.css"),
        html.button("My Button!"),
    )
