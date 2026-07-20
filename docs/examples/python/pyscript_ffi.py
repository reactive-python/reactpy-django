from pyscript import document, window
from reactpy import component, html


@component
def root():
    def on_click(event):
        my_element = document.querySelector("#example")
        my_element.innerText = window.location.hostname

    return html.div(
        {"id": "example"},
        html.button({"onClick": on_click}, "Click Me!"),
    )
