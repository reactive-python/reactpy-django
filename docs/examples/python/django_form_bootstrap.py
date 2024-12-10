from reactpy import component

from example.forms import MyForm
from reactpy_django.components import django_form


@component
def basic_form():
    return django_form(MyForm, form_template="bootstrap_form.html")
