from django.apps import AppConfig
from reactpy_django.utils import register_iframe

from . import views


class ExampleAppConfig(AppConfig):
    name = "example"

    def ready(self):
        register_iframe(views.hello_world)
