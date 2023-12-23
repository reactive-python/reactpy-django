from django.urls import re_path

from test_app.router.views import router

urlpatterns = [
    re_path(r"^router/(?P<path>.*)/?$", router),
]
