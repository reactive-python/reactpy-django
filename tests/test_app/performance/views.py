from django.shortcuts import render


def renders_per_second(request, count: int = 1):
    return render(request, "renders_per_second.html", {"count": range(max(count, 1))})
