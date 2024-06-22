from django.shortcuts import render
from reactpy import html


def index(request):
    return render(
        request,
        "my_template.html",
        context={"my_initial_object": html.div("Loading ...")},
    )
