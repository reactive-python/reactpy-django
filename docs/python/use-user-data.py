from reactpy import component, html
from reactpy_django.hooks import use_user_data


@component
def my_component():
    query, mutation = use_user_data()

    def on_submit(event):
        if event["key"] == "Enter" and query.data:
            new_key = str(len(query.data))
            mutation({**query.data, new_key: event["target"]["value"]})

    return html.div(
        html.div(f"Data: {query.data}"),
        html.div(f"Loading: {query.loading | mutation.loading}"),
        html.div(f"Error(s): {query.error} {mutation.error}"),
        html.input({"on_key_press": on_submit}),
    )
