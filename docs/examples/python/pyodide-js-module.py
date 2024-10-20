import js
from reactpy import component, html


@component
def root():

    def onClick(event):
        js.document.title = "New window title"

    return html.button({"onClick": onClick}, "Click Me!")
