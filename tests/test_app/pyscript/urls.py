from django.urls import re_path

from test_app.pyscript.views import pyscript

urlpatterns = [
    re_path(r"^pyscript/(?P<path>.*)/?$", pyscript),
]
