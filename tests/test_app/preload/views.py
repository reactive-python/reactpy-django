from django.shortcuts import render


def preload(request):
    return render(request, "preload.html", {})
