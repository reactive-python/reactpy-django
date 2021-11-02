from django.apps import AppConfig

from django_idom.utils import ComponentPreloader


class DjangoIdomConfig(AppConfig):
    name = "django_idom"

    def ready(self):
        # Populate the IDOM component registry when Django is ready
        ComponentPreloader().register_all()
