from django.urls import path

from test_app.channel_layers.views import channel_layers

urlpatterns = [
    path("channel-layers/", channel_layers),
]
