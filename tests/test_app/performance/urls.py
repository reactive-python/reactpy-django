from django.urls import path

from .views import events_per_second, renders_per_second, time_to_load


urlpatterns = [
    path("rps/", renders_per_second),
    path("rps/<int:count>", renders_per_second),
    path("ttl/", time_to_load),
    path("ttl/<int:count>", time_to_load),
    path("eps/", events_per_second),
    path("eps/<int:count>", events_per_second),
]
