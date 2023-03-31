from django.apps import AppConfig

from reactpy_django.utils import ComponentPreloader


class ReactPyConfig(AppConfig):
    name = "reactpy_django"

    def ready(self):
        # Populate the ReactPy component registry when Django is ready
        ComponentPreloader().run()
