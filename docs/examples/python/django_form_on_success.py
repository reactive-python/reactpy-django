from reactpy import component, hooks, html
from reactpy_router import navigate

from example.forms import MyForm
from reactpy_django.components import django_form
from reactpy_django.types import FormEventData


@component
def basic_form():
    success, set_success = hooks.use_state(False)

    def on_success(event: FormEventData):
        set_success(True)

    if not success:
        children = [html.input({"type": "submit"})]
        return django_form(MyForm, on_success=on_success, bottom_children=children)

    return navigate("/homepage")
