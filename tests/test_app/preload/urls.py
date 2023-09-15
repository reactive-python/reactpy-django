from django.urls import path

from .views import preload

urlpatterns = [
    path("preload/", preload),
]
