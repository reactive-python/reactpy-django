from django.urls import path

from .views import renders_per_second

urlpatterns = [
    path("rps/", renders_per_second),
    path("rps/<int:count>", renders_per_second),
]
