from reactpy import component, html
from reactpy_django.components import python_to_pyscript


@component
def embed():
    return html.div(
        {"className": "embeddable"},
        python_to_pyscript("./test_app/pyscript/components/child_embed.py"),
    )
