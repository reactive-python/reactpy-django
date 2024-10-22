from reactpy import component, html
from reactpy_django.hooks import use_mutation


def execute_thread_safe_mutation(text):
    """This is an example mutation function that does some thread-safe operation."""
    pass


@component
def my_component():
    item_mutation = use_mutation(
        execute_thread_safe_mutation,
        thread_sensitive=False,
    )

    def submit_event(event):
        if event["key"] == "Enter":
            item_mutation(text=event["target"]["value"])

    if item_mutation.loading or item_mutation.error:
        mutation_status = html.h2("Doing something...")
    elif item_mutation.error:
        mutation_status = html.h2("Error!")
    else:
        mutation_status = html.h2("Done.")

    return html.div(
        html.input({"type": "text", "on_key_down": submit_event}),
        mutation_status,
    )
