from django.shortcuts import render


def index(request):
    return render(
        request,
        "my_template.html",
        context={"my_config_object": {"experimental_create_proxy": "auto"}},
    )
