from reactpy import component, html, use_state
from reactpy_django.components import python_to_pyscript


@component
def embed():
    return html.div(
        {"className": "embeddable"},
        python_to_pyscript("./test_app/pyscript/components/child_embed.py"),
    )


@component
def toggeable_embed():
    state, set_state = use_state(False)

    if not state:
        return html.div(
            {"className": "embeddable"},
            html.button(
                {"onClick": lambda x: set_state(not state)},
                "Click to show/hide",
            ),
        )

    return html.div(
        {"className": "embeddable"},
        html.button(
            {"onClick": lambda x: set_state(not state)},
            "Click to show/hide",
        ),
        python_to_pyscript("./test_app/pyscript/components/child_embed.py"),
    )
