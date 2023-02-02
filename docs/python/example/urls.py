from django.urls import path
from example import views


urlpatterns = [
    path("example/", views.index),
]
