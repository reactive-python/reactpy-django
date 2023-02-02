from django.shortcuts import render


def example_view(request):
    context_vars = {"dont_do_this": "example_project.my_app.components.hello_world"}
    return render(request, "my-template.html", context_vars)
