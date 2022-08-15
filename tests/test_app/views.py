from django.shortcuts import render
from django.views.generic import TemplateView


def base_template(request):
    context = {}
    return render(request, "base.html", context)


def view_to_component_sync_func(request):
    return render(
        request,
        "view_to_component.html",
        {"test_name": view_to_component_sync_func.__name__},
    )


async def view_to_component_async_func(request):
    return render(
        request,
        "view_to_component.html",
        {"test_name": view_to_component_async_func.__name__},
    )


class ViewToComponentSyncClass(TemplateView):
    template_name = "view_to_component.html"

    def get_context_data(self, **kwargs):
        return {"test_name": ViewToComponentSyncClass.__name__}


def view_to_component_sync_func_compatibility(request):
    return render(
        request,
        "view_to_component.html",
        {"test_name": view_to_component_sync_func_compatibility.__name__},
    )


def view_to_component_script(request):
    return render(
        request,
        "view_to_component_script.html",
        {"test_name": view_to_component_script.__name__, "status": "Fail"},
    )
