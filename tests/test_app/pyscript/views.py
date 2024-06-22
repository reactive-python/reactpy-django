from django.shortcuts import render


def pyscript(request, path=None):
    return render(request, "pyscript.html", {})
