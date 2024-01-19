from django.shortcuts import render


def example_view(request):
    context_vars = {"my_variable": "example_project.my_app.components.hello_world"}
    return render(request, "my-template.html", context_vars)
