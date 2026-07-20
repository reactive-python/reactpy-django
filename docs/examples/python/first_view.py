from django.shortcuts import render


def index(request):
    return render(request, "my_template.html")
