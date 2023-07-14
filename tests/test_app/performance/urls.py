from django.urls import path

from .views import (
    events_per_second,
    mixed_time_to_load,
    net_io_time_to_load,
    renders_per_second,
    time_to_load,
)

urlpatterns = [
    path("rps/", renders_per_second),
    path("rps/<int:count>", renders_per_second),
    path("net_ttl/", net_io_time_to_load),
    path("net_ttl/<int:count>", net_io_time_to_load),
    path("mixed_ttl/", mixed_time_to_load),
    path("mixed_ttl/<int:count>", mixed_time_to_load),
    path("ttl/", time_to_load),
    path("ttl/<int:count>", time_to_load),
    path("eps/", events_per_second),
    path("eps/<int:count>", events_per_second),
]
