"""Jinja2 environment configuration for the test app."""

from jinja2 import Environment


def environment(**options):
    """Create a Jinja2 environment with the ReactPy extension loaded."""
    from reactpy_django.templatetags.jinja import ReactPyExtension

    env = Environment(**options)
    env.add_extension(ReactPyExtension)
    return env
