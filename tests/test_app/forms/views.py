from django.shortcuts import render


def form(request):
    return render(request, "form.html", {})


def bootstrap_form(request):
    return render(request, "bootstrap_form.html", {})


def databased_backed_form(request):
    return render(request, "database_backed_form.html", {})
