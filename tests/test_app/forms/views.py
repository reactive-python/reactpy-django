from django.shortcuts import render


def form(request):
    return render(request, "form.html", {})


def bootstrap_form(request):
    return render(request, "bootstrap_form.html", {})


def model_form(request):
    return render(request, "model_form.html", {})


def sync_event_form(request):
    return render(request, "sync_event_form.html", {})


def async_event_form(request):
    return render(request, "async_event_form.html", {})
