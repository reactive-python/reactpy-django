from reactpy import component, html
from reactpy_django.hooks import use_mutation
from reactpy_django.types import MutationOptions


def execute_thread_safe_mutation():
    """This is an example mutation function that does some thread-safe operation."""
    pass


@component
def my_component():
    item_mutation = use_mutation(
        MutationOptions(thread_sensitive=False),
        execute_thread_safe_mutation,
    )

    def submit_event(event):
        if event["key"] == "Enter":
            item_mutation.execute(text=event["target"]["value"])

    if item_mutation.loading or item_mutation.error:
        mutation_status = html.h2("Doing something...")
    elif item_mutation.error:
        mutation_status = html.h2("Error!")
    else:
        mutation_status = html.h2("Done.")

    return html.div(
        html.input({"type": "text", "onKeyDown": submit_event}),
        mutation_status,
    )
