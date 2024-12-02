from typing import ClassVar

from reactpy_django.config import REACTPY_DATABASE


class Router:
    """
    A router to control all database operations on models in the
    auth and contenttypes applications.
    """

    route_app_labels: ClassVar[set[str]] = {"reactpy_django"}

    def db_for_read(self, model, **hints):
        """Attempts to read go to REACTPY_DATABASE."""
        if model._meta.app_label in self.route_app_labels:
            return REACTPY_DATABASE
        return None

    def db_for_write(self, model, **hints):
        """Attempts to write go to REACTPY_DATABASE."""
        if model._meta.app_label in self.route_app_labels:
            return REACTPY_DATABASE
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Returning `None` only allow relations within the same database.
        https://docs.djangoproject.com/en/stable/topics/db/multi-db/#limitations-of-multiple-databases
        """
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Make sure ReactPy models only appear in REACTPY_DATABASE."""
        return db == REACTPY_DATABASE if app_label in self.route_app_labels else None
