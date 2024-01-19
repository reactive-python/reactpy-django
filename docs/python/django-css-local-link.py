from django.templatetags.static import static
from reactpy import component, html


@component
def my_component():
    return html.div(
        html.link({"rel": "stylesheet", "href": static("css/buttons.css")}),
        html.button("My Button!"),
    )
