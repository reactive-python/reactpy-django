from django.shortcuts import render
from django.views.generic import TemplateView


def base_template(request):
    context = {}
    return render(request, "base.html", context)


def view_to_component(request):
    return render(request, "view_to_component.html", {"test_name": "view_to_component"})


async def view_to_component_async(request):
    return render(
        request, "view_to_component.html", {"test_name": "view_to_component_async"}
    )


class ViewToComponentClass(TemplateView):
    template_name = "view_to_component.html"


def view_to_component_compat(request):
    return render(
        request, "view_to_component.html", {"test_name": "view_to_component_compat"}
    )


def view_to_component_middleware(request):
    return render(
        request, "view_to_component.html", {"test_name": "view_to_component_middleware"}
    )
