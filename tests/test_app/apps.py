import contextlib
import sys

from django.apps import AppConfig
from reactpy_django.utils import register_iframe

from test_app import views


class TestAppConfig(AppConfig):
    name = "test_app"

    def ready(self):
        from django.contrib.auth.models import User

        register_iframe("test_app.views.view_to_component_sync_func_compatibility")
        register_iframe(views.view_to_component_async_func_compatibility)
        register_iframe(views.ViewToComponentSyncClassCompatibility)
        register_iframe(views.ViewToComponentAsyncClassCompatibility)
        register_iframe(views.ViewToComponentTemplateViewClassCompatibility)
        register_iframe(views.view_to_iframe_args)

        if "test" in sys.argv:
            return

        with contextlib.suppress(Exception):
            User.objects.create_superuser(
                username="admin", email="admin@example.com", password="password"
            )
