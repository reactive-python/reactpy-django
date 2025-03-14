import sys

from django.apps import AppConfig

from reactpy_django.utils import register_iframe
from test_app import views


class TestAppConfig(AppConfig):
    name = "test_app"

    def ready(self):
        register_iframe("test_app.views.view_to_iframe_sync_func")
        register_iframe(views.view_to_iframe_async_func)
        register_iframe(views.ViewToIframeSyncClass)
        register_iframe(views.ViewToIframeAsyncClass)
        register_iframe(views.ViewToIframeTemplateViewClass)
        register_iframe(views.view_to_iframe_args)

        if "test" in sys.argv:
            return
