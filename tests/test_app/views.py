import idom
from django.http import HttpResponse
from django.template import loader


def base_template(request):
    template = loader.get_template("base.html")
    context = {}
    return HttpResponse(template.render(context, request))


@idom.component
def HelloWorld():
    return idom.html.h1({"id": "hello-world"}, "Hello World!")
