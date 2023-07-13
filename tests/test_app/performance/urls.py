from django.urls import path

from .views import renders_per_second, time_to_load

urlpatterns = [
    path("rps/", renders_per_second),
    path("rps/<int:count>", renders_per_second),
    path("ttl/", time_to_load),
    path("ttl/<int:count>", time_to_load),
]
