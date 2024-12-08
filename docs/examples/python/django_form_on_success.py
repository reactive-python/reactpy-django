from reactpy import component, hooks, html
from reactpy_router import navigate

from example.forms import MyForm
from reactpy_django.components import django_form
from reactpy_django.types import FormEventData


@component
def basic_form():
    submitted, set_submitted = hooks.use_state(False)

    def on_submit(event: FormEventData):
        """This function will be called when the form is successfully submitted."""
        set_submitted(True)

    if submitted:
        return navigate("/homepage")

    children = [html.input({"type": "submit"})]
    return django_form(MyForm, on_success=on_submit, bottom_children=children)
