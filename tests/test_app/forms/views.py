from django.shortcuts import render


def form(request):
    return render(request, "form.html", {})


def bootstrap_form(request):
    return render(request, "bootstrap_form.html", {})
