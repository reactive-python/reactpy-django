import inspect
from itertools import cycle

from channels.db import database_sync_to_async
from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import TemplateView, View

from .types import TestObject


def base_template(request):
    return render(request, "base.html", {"my_object": TestObject(1)})


def errors_template(request):
    return render(request, "errors.html", {})


def host_port_template(request: HttpRequest, port: int):
    host = request.get_host().replace(str(request.get_port()), str(port))
    return render(request, "host_port.html", {"new_host": host})


def host_port_roundrobin_template(
    request: HttpRequest, port1: int, port2: int, count: int = 1
):
    from reactpy_django import config

    # Override ReactPy config to use round-robin hosts
    original = config.REACTPY_DEFAULT_HOSTS
    config.REACTPY_DEFAULT_HOSTS = cycle(
        [
            f"{request.get_host().split(':')[0]}:{port1}",
            f"{request.get_host().split(':')[0]}:{port2}",
        ]
    )
    html = render(
        request,
        "host_port_roundrobin.html",
        {"count": range(max(count, 1))},
    )

    # Reset ReactPy config
    config.REACTPY_DEFAULT_HOSTS = original
    return html


def view_to_component_sync_func(request):
    return render(
        request,
        "view_to_component.html",
        {"test_name": inspect.currentframe().f_code.co_name},  # type:ignore
    )


async def view_to_component_async_func(request):
    return render(
        request,
        "view_to_component.html",
        {"test_name": inspect.currentframe().f_code.co_name},  # type:ignore
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
        {"test_name": inspect.currentframe().f_code.co_name},  # type:ignore
    )


async def view_to_component_async_func_compatibility(request):
    return await database_sync_to_async(render)(
        request,
        "view_to_component.html",
        {"test_name": inspect.currentframe().f_code.co_name},  # type:ignore
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


def view_to_iframe_args(request, arg1, arg2, kwarg1=None, kwarg2=None):
    success = (
        arg1 == "Arg1" and arg2 == "Arg2" and kwarg1 == "Kwarg1" and kwarg2 == "Kwarg2"
    )

    return render(
        request,
        "view_to_component.html",
        {
            "test_name": inspect.currentframe().f_code.co_name,  # type:ignore
            "status": "Success" if success else "false",
        },
    )


def view_to_component_script(request):
    return render(
        request,
        "view_to_component_script.html",
        {
            "test_name": inspect.currentframe().f_code.co_name,  # type:ignore
            "status": "false",
        },
    )


def view_to_component_request(request):
    if request.method == "POST":
        return render(
            request,
            "view_to_component.html",
            {"test_name": inspect.currentframe().f_code.co_name},  # type:ignore
        )

    return render(
        request,
        "view_to_component.html",
        {
            "test_name": inspect.currentframe().f_code.co_name,  # type:ignore
            "status": "false",
        },
    )


def view_to_component_args(request, success):
    return render(
        request,
        "view_to_component.html",
        {
            "test_name": inspect.currentframe().f_code.co_name,  # type:ignore
            "status": success,
        },
    )


def view_to_component_kwargs(request, success="false"):
    return render(
        request,
        "view_to_component.html",
        {
            "test_name": inspect.currentframe().f_code.co_name,  # type:ignore
            "status": success,
        },
    )
