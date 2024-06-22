from reactpy import component, html
from reactpy_django.html import pyscript

example_source_code = """
import js

js.console.log("Hello, World!")
"""


@component
def server_side_component():
    return html.div(
        pyscript(example_source_code.strip()),
    )
