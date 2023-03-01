from django.urls import include, path


urlpatterns = [
    path("reactpy/", include("django_reactpy.http.urls")),
    ...,
]
