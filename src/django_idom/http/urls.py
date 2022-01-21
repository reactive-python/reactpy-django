from django.urls import path

from . import views


app_name = "idom"

urlpatterns = [
    path(
        "web_module/<path:file>",
        views.web_modules_file,
        name="web_modules",
    )
]
