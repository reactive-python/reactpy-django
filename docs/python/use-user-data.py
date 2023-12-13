from reactpy import component, html
from reactpy_django.hooks import use_user_data


@component
def my_component():
    user_data, set_user_data = use_user_data()

    async def on_submit(event):
        if event["key"] == "Enter":
            key = str(len(user_data.current))
            merged_data = user_data.current | {key: event["target"]["value"]}
            set_user_data(merged_data)

    return html.div(
        html.div(f"Data: {user_data.current}"),
        html.div(f"Loading: {user_data.loading | set_user_data.loading}"),
        html.div(f"Error(s): {user_data.error} {set_user_data.error}"),
        html.input({"on_key_press": on_submit}),
    )
