from django.http import HttpResponse
from django.views import View
from django_reactpy.components import view_to_component
from reactpy import component, html


class HelloWorldView(View):
    def get(self, request):
        return HttpResponse("Hello World!")


vtc = view_to_component(HelloWorldView)


@component
def my_component():
    return html.div(
        vtc(),
    )
