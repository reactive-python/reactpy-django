from reactpy import component, hooks, html

from reactpy_django.components import django_form

from .forms import BasicForm, DatabaseBackedForm, EventForm


@component
def basic_form():
    return django_form(BasicForm, bottom_children=(html.input({"type": "submit"}),))


@component
def bootstrap_form():
    return django_form(
        BasicForm,
        extra_props={"style": {"maxWidth": "600px", "margin": "auto"}},
        form_template="bootstrap_form_template.html",
    )


@component
def database_backed_form():
    return django_form(DatabaseBackedForm, bottom_children=(html.input({"type": "submit"}),))


@component
def sync_event_form():
    success, set_success = hooks.use_state(False)
    error, set_error = hooks.use_state(False)
    receive_data, set_receive_data = hooks.use_state(False)
    change, set_change = hooks.use_state(False)

    def on_success(event):
        set_success(True)

    def on_error(event):
        set_error(True)

    def on_receive_data(event):
        set_receive_data(True)

    def on_change(event):
        set_change(True)

    return django_form(
        EventForm,
        on_success=on_success,
        on_error=on_error,
        on_receive_data=on_receive_data,
        on_change=on_change,
        top_children=[
            html.div({"id": "success", "data-value": success}, f"Success: {success}"),
            html.div({"id": "error", "data-value": error}, f"Error: {error}"),
            html.div({"id": "receive_data", "data-value": receive_data}, f"Receive Data: {receive_data}"),
            html.div({"id": "change", "data-value": change}, f"Change: {change}"),
        ],
        bottom_children=[html.input({"type": "submit"})],
    )


@component
def async_event_form():
    success, set_success = hooks.use_state(False)
    error, set_error = hooks.use_state(False)
    receive_data, set_receive_data = hooks.use_state(False)
    change, set_change = hooks.use_state(False)

    async def on_success(event):
        set_success(True)

    async def on_error(event):
        set_error(True)

    async def on_receive_data(event):
        set_receive_data(True)

    async def on_change(event):
        set_change(True)

    return django_form(
        EventForm,
        on_success=on_success,
        on_error=on_error,
        on_receive_data=on_receive_data,
        on_change=on_change,
        top_children=[
            html.div({"id": "success", "data-value": success}, f"Success: {success}"),
            html.div({"id": "error", "data-value": error}, f"Error: {error}"),
            html.div({"id": "receive_data", "data-value": receive_data}, f"Receive Data: {receive_data}"),
            html.div({"id": "change", "data-value": change}, f"Change: {change}"),
        ],
        bottom_children=[html.input({"type": "submit"})],
    )
