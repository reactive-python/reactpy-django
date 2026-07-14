from reactpy import component, html

example_source_code = """
import js

js.console.log("Hello, World!")
"""


@component
def server_side_component():
    return html.py_script(example_source_code.strip())
