from idom import component, html

from django_idom.components import django_js


@component
def my_component():
    return html.div(
        html.button("My Button!"),
        django_js("js/scripts.js"),
    )
