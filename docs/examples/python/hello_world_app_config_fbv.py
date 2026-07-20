from django.apps import AppConfig

from example import views
from reactpy_django.utils import register_iframe


class ExampleAppConfig(AppConfig):
    name = "example"

    def ready(self):
        register_iframe(views.hello_world)
