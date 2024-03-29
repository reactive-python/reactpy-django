from django.templatetags.static import static
from reactpy import component, html


@component
def my_component():
    return html.div(
        html.script({"src": static("js/scripts.js")}),
        html.button("My Button!"),
    )
