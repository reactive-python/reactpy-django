from django.urls import path

from . import views

app_name = "reactpy"

urlpatterns = [
    path(
        "web_module/<path:file>",
        views.web_modules_file,
        name="web_modules",
    ),
    path(
        "iframe/<str:dotted_path>",
        views.view_to_iframe,
        name="view_to_iframe",
    ),
]
