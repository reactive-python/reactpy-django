from reactpy import component, html
from reactpy_django.hooks import use_user_data


@component
def my_component():
    user_data = use_user_data(
        default_data={
            "basic_example": "123",
            "computed_example_sync": sync_default,
            "computed_example_async": async_default,
        }
    )

    return html.div(
        html.div(f"Data: {user_data.query.data}"),
    )


def sync_default():
    return ...


async def async_default():
    return ...
