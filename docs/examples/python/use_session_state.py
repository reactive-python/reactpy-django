from reactpy import component, html

from reactpy_django.hooks import use_session_state


@component
def my_component():
    count, set_count = use_session_state(0, key="counter")

    return html.button(
        {"onClick": lambda _: set_count(count + 1)},
        f"Count: {count}",
    )
