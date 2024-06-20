from reactpy import component, html, use_state


@component
def root():
    value, set_value = use_state(0)
    return html.article(
        "This was embedded via a server-side component.",
        html.div(
            {"className": "grid"},
            html.button({"on_click": lambda event: set_value(value + 1)}, "+"),
            html.button({"on_click": lambda event: set_value(value - 1)}, "-"),
        ),
        "Current value",
        html.pre({"style": {"font-style": "bold"}}, str(value)),
    )
