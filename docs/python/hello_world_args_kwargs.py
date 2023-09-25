from django.http import HttpResponse


def hello_world(request, arg1, arg2, kwarg1=None, kwarg2=None):
    return HttpResponse(f"Hello World! {arg1} {arg2} {kwarg1} {kwarg2}")
