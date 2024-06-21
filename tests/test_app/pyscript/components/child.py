from reactpy import component, html, use_state


@component
def root():
    value, set_value = use_state(0)
    return html.article(
        {"id": "child"},
        "This was embedded via a server-side component.",
        html.div(
            {"className": "grid"},
            html.button(
                {"className": "plus", "on_click": lambda event: set_value(value + 1)},
                "+",
            ),
            html.button(
                {"className": "minus", "on_click": lambda event: set_value(value - 1)},
                "-",
            ),
        ),
        "Current value",
        html.pre(
            {"style": {"font-style": "bold"}, "data-value": str(value)}, str(value)
        ),
    )
