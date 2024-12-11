from django.urls import path

from . import views

urlpatterns = [
    path("form/", views.form),
    path("form/bootstrap/", views.bootstrap_form),
    path("form/model/", views.model_form),
    path("form/sync_event/", views.sync_event_form),
    path("form/async_event/", views.async_event_form),
]
