from django.apps import AppConfig
from reactpy_django.utils import register_iframe

from test_app import views


class TestAppConfig(AppConfig):
    name = "test_app"

    def ready(self):
        register_iframe("test_app.views.view_to_component_sync_func_compatibility")
        register_iframe(views.view_to_component_async_func_compatibility)
        register_iframe(views.ViewToComponentSyncClassCompatibility)
        register_iframe(views.ViewToComponentAsyncClassCompatibility)
        register_iframe(views.ViewToComponentTemplateViewClassCompatibility)
        register_iframe(views.view_to_iframe_args)
