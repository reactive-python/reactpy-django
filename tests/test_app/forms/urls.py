from django.urls import path

from . import views

urlpatterns = [
    path("form/", views.form),
    path("form/bootstrap/", views.bootstrap_form),
    path("form/database/", views.databased_backed_form),
]
