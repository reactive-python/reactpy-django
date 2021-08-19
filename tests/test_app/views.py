from django.http import HttpResponse
from django.template import loader


def base_template(request):
    context = {}
    return HttpResponse(loader.get_template("base.html").render(context, request))
