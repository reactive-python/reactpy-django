from django.urls import include, path


urlpatterns = [
    ...,
    path("reactpy/", include("reactpy_django.http.urls")),
]
