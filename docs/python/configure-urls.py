from django.urls import include, path


urlpatterns = [
    path("idom/", include("django_idom.http.urls")),
    ...,
]
