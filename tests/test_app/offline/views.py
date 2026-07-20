from django.shortcuts import render


def offline(request):
    return render(request, "offline.html", {})
