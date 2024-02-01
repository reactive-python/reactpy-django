from django.shortcuts import render


def channel_layers(request, path=None):
    return render(request, "channel_layers.html", {})
