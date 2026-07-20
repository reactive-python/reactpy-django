from django.contrib.auth import get_user_model
from reactpy import component, html

from reactpy_django.hooks import use_auth, use_user


@component
def my_component():
    auth = use_auth()
    user = use_user()

    async def login_user(event):
        new_user, _created = await get_user_model().objects.aget_or_create(username="ExampleUser")
        await auth.login(new_user)

    async def logout_user(event):
        await auth.logout()

    return html.div(
        f"Current User: {user}",
        html.button({"onClick": login_user}, "Login"),
        html.button({"onClick": logout_user}, "Logout"),
    )
