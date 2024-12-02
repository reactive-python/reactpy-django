import js
from reactpy import component, html


@component
def root():
    def on_click(event):
        js.document.title = "New window title"

    return html.button({"onClick": on_click}, "Click Me!")
