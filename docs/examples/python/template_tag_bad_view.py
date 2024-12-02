from django.shortcuts import render


def example_view(request):
    return render(
        request,
        "my_template.html",
        context={"my_variable": "example_project.my_app.components.hello_world"},
    )
