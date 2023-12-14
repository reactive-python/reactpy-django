from reactpy import component, html
from reactpy_django.hooks import use_user_data


@component
def my_component():
    data, set_data = use_user_data()

    async def on_submit(event):
        if event["key"] == "Enter" and data.current:
            key = str(len(data.current))
            merged_data = data.current | {key: event["target"]["value"]}
            set_data(merged_data)

    return html.div(
        html.div(f"Data: {data.current}"),
        html.div(f"Loading: {data.loading | set_data.loading}"),
        html.div(f"Error(s): {data.error} {set_data.error}"),
        html.input({"on_key_press": on_submit}),
    )
