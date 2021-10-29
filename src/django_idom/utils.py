import os
from fnmatch import fnmatch
from importlib import import_module

from django.template import engines
from django.template.loader import get_template
from django.utils.encoding import smart_str


class TemplateLoader:
    def render_all(self):
        """Renders all available HTML templates known to Django."""
        # Get all template folder paths
        paths = self._get_paths()

        # Get all HTML template files
        templates = self._get_templates(paths)

        # Render all templates
        self._render_templates(templates)

    def _get_loaders(self):
        """Obtains currently configured template loaders."""
        template_source_loaders = []
        for e in engines.all():
            if hasattr(e, "engine"):
                template_source_loaders.extend(
                    e.engine.get_template_loaders(e.engine.loaders)
                )
        loaders = []
        for loader in template_source_loaders:
            if hasattr(loader, "loaders"):
                loaders.extend(loader.loaders)
            else:
                loaders.append(loader)
        return loaders

    def _get_paths(self):
        """Obtains a set of all template directories."""
        paths = set()
        for loader in self._get_loaders():
            try:
                module = import_module(loader.__module__)
                get_template_sources = getattr(module, "get_template_sources", None)
                if get_template_sources is None:
                    get_template_sources = loader.get_template_sources
                paths.update(smart_str(origin) for origin in get_template_sources(""))
            except (ImportError, AttributeError, TypeError):
                pass

        return paths

    def _get_templates(self, paths):
        """Obtains a set of all HTML template paths."""
        extensions = [".html"]
        templates = set()
        for path in paths:
            for root, dirs, files in os.walk(path, followlinks=False):
                templates.update(
                    os.path.relpath(os.path.join(root, name), path)
                    for name in files
                    if not name.startswith(".")
                    and any(fnmatch(name, "*%s" % glob) for glob in extensions)
                )

        return templates

    def _render_templates(self, templates):
        """Renders all templates. Templates with invalid syntax are ignored."""
        for template in templates:
            try:
                get_template(template).render({"csrf_token": "123"})
            except Exception:
                pass
