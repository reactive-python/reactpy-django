from reactpy import component, html

from example.forms import MyForm
from reactpy_django.components import django_form


@component
def basic_form():
    children = [html.input({"type": "submit"})]
    return django_form(MyForm, bottom_children=children)
