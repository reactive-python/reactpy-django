from reactpy import component, html

from reactpy_django.components import django_form

from .forms import BasicForm, DatabaseBackedForm


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
