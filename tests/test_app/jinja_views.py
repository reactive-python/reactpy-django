"""Jinja2 template views for the test app."""

from django.shortcuts import render

from .types import TestObject


def jinja_base_template(request):
    """Render the Jinja2 version of the base template."""
    return render(request, "base.html", {"my_object": TestObject(1)}, using="jinja2")


def jinja_errors_template(request):
    """Render the Jinja2 version of the errors template."""
    return render(request, "errors.html", {}, using="jinja2")
