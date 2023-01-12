import contextlib

from django.apps import AppConfig
from django.db.utils import OperationalError

from django_idom.utils import ComponentPreloader, db_cleanup


class DjangoIdomConfig(AppConfig):
    name = "django_idom"

    def ready(self):
        # Populate the IDOM component registry when Django is ready
        ComponentPreloader().run()

        # Delete expired database entries
        # Suppress exceptions to avoid issues with `manage.py` commands such as
        # `test`, `migrate`, `makemigrations`, or any custom user created commands
        # where the database may not be preconfigured.
        with contextlib.suppress(OperationalError):
            db_cleanup(immediate=True)
