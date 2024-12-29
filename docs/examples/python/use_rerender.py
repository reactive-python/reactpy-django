from uuid import uuid4

from reactpy import component, html

from reactpy_django.hooks import use_rerender


@component
def my_component():
    rerender = use_rerender()

    def on_click():
        rerender()

    return html.div(f"UUID: {uuid4()}", html.button({"onClick": on_click}, "Rerender"))
