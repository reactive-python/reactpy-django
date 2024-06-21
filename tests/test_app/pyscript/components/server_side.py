from reactpy import component, html, use_state
from reactpy_django.components import python_to_pyscript


@component
def parent():
    return html.div(
        {"id": "parent"},
        python_to_pyscript("./test_app/pyscript/components/child.py"),
    )


@component
def parent_toggle():
    state, set_state = use_state(False)

    if not state:
        return html.div(
            {"id": "parent-toggle"},
            html.button(
                {"onClick": lambda x: set_state(not state)},
                "Click to show/hide",
            ),
        )

    return html.div(
        {"id": "parent-toggle"},
        html.button(
            {"onClick": lambda x: set_state(not state)},
            "Click to show/hide",
        ),
        python_to_pyscript("./test_app/pyscript/components/child.py"),
    )
