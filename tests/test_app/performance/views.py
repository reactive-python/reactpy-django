from django.shortcuts import render


def renders_per_second(request):
    return render(request, "renders_per_second.html", {})
