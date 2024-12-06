from django.urls import path

from . import views

urlpatterns = [
    path("form/", views.form),
    path("form/bootstrap/", views.bootstrap_form),
]
