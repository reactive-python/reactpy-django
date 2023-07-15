from django.urls import path

from .views import (
    event_renders_per_second,
    event_timing,
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
    path("erps/", event_renders_per_second),
    path("erps/<int:count>", event_renders_per_second),
    path("et/", event_timing),
    path("et/<int:count>", event_timing),
]
