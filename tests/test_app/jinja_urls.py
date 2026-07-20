"""URL patterns for Jinja2 template views."""

from django.urls import path

from . import jinja_views

urlpatterns = [
    path("", jinja_views.jinja_base_template, name="jinja_base_template"),
    path("errors/", jinja_views.jinja_errors_template, name="jinja_errors_template"),
]
