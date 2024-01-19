from django.urls import path

from .views import offline

urlpatterns = [
    path("offline/", offline),
]
