from django.apps import AppConfig
from .utils import TemplateLoader


class HomeConfig(AppConfig):
    name = "django_idom"

    def ready(self):
        # Render all templates once when Django is ready
        # in order to populate the IDOM component registry
        TemplateLoader().render_all()
