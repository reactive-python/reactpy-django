from django.apps import AppConfig

from reactpy_django.utils import RootComponentFinder


class ReactPyConfig(AppConfig):
    name = "reactpy_django"

    def ready(self):
        # Populate the ReactPy component registry when Django is ready
        RootComponentFinder().run()

        # Mirror the ReactPy wheel into our static directory so PyScript
        # pages can fetch it. This is safe under multi-process servers:
        # see ``reactpy_django/_static_wheels.py`` for the locking and
        # atomic-write guarantees.
        #
        # Importing the module here (rather than at the top of the
        # file) avoids a circular import on first Django startup and
        # keeps the cost off the import path of consumers that never
        # trigger ``ready()``.
        from reactpy_django import _static_wheels

        try:
            _static_wheels.sync_static_wheels()
        except Exception:  # pragma: no cover - defensive
            # Never let a static-file sync failure break the server.
            # Worst case the PyScript page shows a "wheel not found"
            # error; the rest of the app keeps working.
            import logging

            logging.getLogger(__name__).exception("Failed to mirror ReactPy wheel into static directory")
