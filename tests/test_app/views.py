import inspect

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
        {"test_name": inspect.currentframe().f_code.co_name},
    )


async def view_to_component_async_func(request):
    return render(
        request,
        "view_to_component.html",
        {"test_name": inspect.currentframe().f_code.co_name},
    )


class ViewToComponentSyncClass(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "view_to_component.html",
            {"test_name": self.__class__.__name__},
        )


class ViewToComponentAsyncClass(View):
    async def get(self, request, *args, **kwargs):
        return await database_sync_to_async(render)(
            request,
            "view_to_component.html",
            {"test_name": self.__class__.__name__},
        )


class ViewToComponentTemplateViewClass(TemplateView):
    template_name = "view_to_component.html"

    def get_context_data(self, **kwargs):
        return {"test_name": self.__class__.__name__}


def view_to_component_sync_func_compatibility(request):
    return render(
        request,
        "view_to_component.html",
        {"test_name": inspect.currentframe().f_code.co_name},
    )


async def view_to_component_async_func_compatibility(request):
    return await database_sync_to_async(render)(
        request,
        "view_to_component.html",
        {"test_name": inspect.currentframe().f_code.co_name},
    )


class ViewToComponentSyncClassCompatibility(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "view_to_component.html",
            {"test_name": self.__class__.__name__},
        )


class ViewToComponentAsyncClassCompatibility(View):
    async def get(self, request, *args, **kwargs):
        return await database_sync_to_async(render)(
            request,
            "view_to_component.html",
            {"test_name": self.__class__.__name__},
        )


class ViewToComponentTemplateViewClassCompatibility(TemplateView):
    template_name = "view_to_component.html"

    def get_context_data(self, **kwargs):
        return {"test_name": self.__class__.__name__}


def view_to_component_script(request):
    return render(
        request,
        "view_to_component_script.html",
        {
            "test_name": inspect.currentframe().f_code.co_name,
            "status": "false",
        },
    )


def view_to_component_request(request):
    if request.method == "POST":
        return render(
            request,
            "view_to_component.html",
            {"test_name": inspect.currentframe().f_code.co_name},
        )

    return render(
        request,
        "view_to_component.html",
        {
            "test_name": inspect.currentframe().f_code.co_name,
            "status": "false",
            "success": "false",
        },
    )


def view_to_component_args(request, success):
    return render(
        request,
        "view_to_component.html",
        {"test_name": inspect.currentframe().f_code.co_name, "status": success},
    )


def view_to_component_kwargs(request, success="false"):
    return render(
        request,
        "view_to_component.html",
        {"test_name": inspect.currentframe().f_code.co_name, "status": success},
    )
