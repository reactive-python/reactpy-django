import logging

from django.apps import AppConfig
from django.db.utils import DatabaseError
from django_reactpy.utils import ComponentPreloader, db_cleanup


_logger = logging.getLogger(__name__)


class ReactPyConfig(AppConfig):
    name = "django_reactpy"

    def ready(self):
        # Populate the ReactPy component registry when Django is ready
        ComponentPreloader().run()

        # Delete expired database entries
        # Suppress exceptions to avoid issues with `manage.py` commands such as
        # `test`, `migrate`, `makemigrations`, or any custom user created commands
        # where the database may not be ready.
        try:
            db_cleanup(immediate=True)
        except DatabaseError:
            _logger.debug(
                "Could not access ReactPy database at startup. Skipping cleanup..."
            )
