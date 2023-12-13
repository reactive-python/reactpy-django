from reactpy import component, html
from reactpy_django.hooks import use_user_data


@component
def my_component():
    user_data, set_user_data = use_user_data()

    async def on_submit(event):
        if user_data.current is None:
            raise ValueError("User data not loaded or user is anonymous.")

        if event["key"] == "Enter":
            num = len(user_data.current)
            set_user_data(user_data.current | {f"#{num}": event["target"]["value"]})

    return html.div(
        html.div(f"Data: {user_data.current}"),
        html.div(f"Loading: {user_data.loading | set_user_data.loading}"),
        html.div(f"Error(s): {user_data.error} {set_user_data.error}"),
        html.input({"on_key_press": on_submit}),
    )
