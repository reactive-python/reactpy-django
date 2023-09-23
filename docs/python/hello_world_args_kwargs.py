from django.http import HttpResponse


def hello_world(request, arg1, arg2, key1=None, key2=None):
    return HttpResponse(f"Hello World! {arg1} {arg2} {key1} {key2}")
