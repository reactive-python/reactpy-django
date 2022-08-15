from channels.db import database_sync_to_async
from django.shortcuts import render
from django.views.generic import TemplateView, View


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


class ViewToComponentSyncClass(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "view_to_component.html",
            {"test_name": ViewToComponentSyncClass.__name__},
        )


class ViewToComponentAsyncClass(View):
    async def get(self, request, *args, **kwargs):
        return await database_sync_to_async(render)(
            request,
            "view_to_component.html",
            {"test_name": ViewToComponentAsyncClass.__name__},
        )


class ViewToComponentTemplateViewClass(TemplateView):
    template_name = "view_to_component.html"

    def get_context_data(self, **kwargs):
        return {"test_name": ViewToComponentTemplateViewClass.__name__}


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
