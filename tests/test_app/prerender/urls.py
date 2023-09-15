from django.urls import path

from .views import prerender

urlpatterns = [
    path("prerender/", prerender),
]
