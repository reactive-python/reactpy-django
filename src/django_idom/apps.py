import sys

from django.apps import AppConfig

from django_idom.utils import ComponentPreloader, db_cleanup


class DjangoIdomConfig(AppConfig):
    name = "django_idom"

    def ready(self):
        # Populate the IDOM component registry when Django is ready
        ComponentPreloader().register_all()

        # Delete expired database entries
        if "test" not in sys.argv:
            db_cleanup(immediate=True)
