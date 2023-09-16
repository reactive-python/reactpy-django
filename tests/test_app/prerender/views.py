from django.shortcuts import render


def prerender(request):
    return render(request, "prerender.html", {})
