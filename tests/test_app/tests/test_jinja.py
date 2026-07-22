"""Tests for Jinja2 template rendering with ReactPy components."""

from django.http import HttpRequest
from django.test import TestCase, override_settings

# Jinja2 template backend configuration to add alongside the default Django templates
JINJA2_TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [],
        "OPTIONS": {
            "environment": "test_app.jinja_env.environment",
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


class Jinja2ComponentTests(TestCase):
    """Verify that ReactPy components render correctly in Jinja2 templates."""

    @override_settings(TEMPLATES=JINJA2_TEMPLATES)
    def test_component_function_available(self):
        """The component function should be available in Jinja2 templates."""
        from jinja2 import Environment

        from reactpy_django.templatetags.jinja import ReactPyExtension

        env = Environment()
        env.add_extension(ReactPyExtension)

        assert "component" in env.globals
        assert callable(env.globals["component"])

    @override_settings(TEMPLATES=JINJA2_TEMPLATES)
    def test_pyscript_component_function_available(self):
        """The pyscript_component function should be available in Jinja2 templates."""
        from jinja2 import Environment

        from reactpy_django.templatetags.jinja import ReactPyExtension

        env = Environment()
        env.add_extension(ReactPyExtension)

        assert "pyscript_component" in env.globals
        assert callable(env.globals["pyscript_component"])

    @override_settings(TEMPLATES=JINJA2_TEMPLATES)
    def test_pyscript_setup_function_available(self):
        """The pyscript_setup function should be available in Jinja2 templates."""
        from jinja2 import Environment

        from reactpy_django.templatetags.jinja import ReactPyExtension

        env = Environment()
        env.add_extension(ReactPyExtension)

        assert "pyscript_setup" in env.globals
        assert callable(env.globals["pyscript_setup"])

    @override_settings(TEMPLATES=JINJA2_TEMPLATES)
    def test_jinja_component_renders_without_error(self):
        """A Jinja2 template containing a component tag should render without error."""
        from django.template import engines

        request = HttpRequest()
        request.method = "GET"

        jinja2_engine = engines["jinja2"]
        template = jinja2_engine.from_string(
            "{{ component('test_app.components.hello_world') }}"
        )
        rendered = template.render({"request": request})
        assert isinstance(rendered, str)
        assert "data-reactpy" in rendered

    @override_settings(TEMPLATES=JINJA2_TEMPLATES)
    def test_jinja_extension_configuration(self):
        """The ReactPyExtension should be configurable via the environment function."""
        from test_app.jinja_env import environment

        env = environment()
        assert "component" in env.globals
        assert callable(env.globals["component"])
        assert "pyscript_component" in env.globals
        assert callable(env.globals["pyscript_component"])
        assert "pyscript_setup" in env.globals
        assert callable(env.globals["pyscript_setup"])
