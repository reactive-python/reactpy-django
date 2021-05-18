from django.template import loader
from django.http import HttpResponse


def base_template(request):
    template = loader.get_template("base.html")
    context = {}
    return HttpResponse(template.render(context, request))
