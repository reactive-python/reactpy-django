from reactpy import component, html
from reactpy_django.hooks import use_root_id


@component
def my_component():
    root_id = use_root_id()

    return html.div(f"Root ID: {root_id}")
