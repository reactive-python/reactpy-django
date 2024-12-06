from reactpy import component, html

from reactpy_django.components import django_form

from .forms import BasicForm


@component
def basic_form(form_template=None):
    return django_form(BasicForm, form_template=form_template, bottom_children=(html.input({"type": "submit"}),))
