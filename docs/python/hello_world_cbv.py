from django.http import HttpResponse
from django.views import View


class HelloWorld(View):
    def get(self, request):
        return HttpResponse("Hello World!")
