from django.apps import AppConfig
from reactpy_django.utils import register_component


class ExampleAppConfig(AppConfig):
    name = "example"

    def ready(self):
        register_component("example_project.my_app.components.hello_world")
