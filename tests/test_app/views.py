from django.shortcuts import render


def base_template(request):
    context = {}
    return render(request, "base.html", context)
