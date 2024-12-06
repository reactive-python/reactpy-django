from django.shortcuts import render


def form(request):
    return render(request, "form.html", {})
