from django.apps import AppConfig
from reactpy_django.utils import register_component


class ExampleConfig(AppConfig):
    def ready(self):
        # Add components to the ReactPy component registry when Django is ready
        register_component("example_project.my_app.components.hello_world")
