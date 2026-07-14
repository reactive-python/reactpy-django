from reactpy import component, html, pyscript_component, use_state


@component
def parent():
    return html.div(
        {"id": "parent"},
        pyscript_component(
            "./test_app/pyscript/components/child.py",
        ),
    )


@component
def parent_toggle():
    state, set_state = use_state(False)

    if not state:
        return html.div(
            {"id": "parent-toggle"},
            html.button(
                {"onClick": lambda _: set_state(not state)},
                "Click to show/hide",
            ),
        )

    return html.div(
        {"id": "parent-toggle"},
        html.button(
            {"onClick": lambda _: set_state(not state)},
            "Click to show/hide",
        ),
        pyscript_component(
            "./test_app/pyscript/components/child.py",
        ),
    )
