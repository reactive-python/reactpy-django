from django.http import HttpResponse


def hello_world(request):
    return HttpResponse('<div id="hello-world"> Hello World! </div>')
