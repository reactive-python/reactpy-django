from django.apps import AppConfig

from django_idom.utils import _ComponentPreloader


class DjangoIdomConfig(AppConfig):
    name = "django_idom"

    def ready(self):
        # Populate the IDOM component registry when Django is ready
        _ComponentPreloader().register_all()
