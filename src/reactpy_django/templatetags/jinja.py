"""
Jinja2 template support for ReactPy-Django.

Provides Jinja2 global functions that mirror the functionality of Django's
``{% component %}``, ``{% pyscript_component %}``, and ``{% pyscript_setup %}``
template tags. These are registered as environment globals so they can be
called directly from Jinja2 templates via ``{{ component(...) }}`` syntax.

To enable, add the extension to your Jinja2 environment configuration:

.. code-block:: python

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.jinja2.Jinja2",
            "DIRS": [...],
            "OPTIONS": {
                "environment": "myproject.jinja_env.environment",
            },
        },
    ]

Then in ``myproject/jinja_env.py``:

.. code-block:: python

    from jinja2 import Environment
    from reactpy_django.templatetags.jinja import ReactPyExtension


    def environment(**options):
        env = Environment(**options)
        env.add_extension(ReactPyExtension)
        return env
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from django.template import RequestContext, loader
from jinja2 import pass_context
from jinja2.ext import Extension

from reactpy_django.templatetags.reactpy import (
    COMPONENT_TEMPLATE,
    PYSCRIPT_COMPONENT_TEMPLATE,
    PYSCRIPT_SETUP_TEMPLATE,
)
from reactpy_django.templatetags.reactpy import (
    component as django_component_tag,
)
from reactpy_django.templatetags.reactpy import (
    pyscript_component as django_pyscript_component_tag,
)
from reactpy_django.templatetags.reactpy import (
    pyscript_setup as django_pyscript_setup_tag,
)

if TYPE_CHECKING:
    from jinja2.runtime import Context
    from reactpy.types import Component, VdomDict

_logger = getLogger(__name__)


class ReactPyExtension(Extension):
    """A Jinja2 extension that adds ReactPy component rendering functions.

    This extension registers the following globals into the Jinja2 environment:

    * ``component`` - Renders a server-side ReactPy component.
    * ``pyscript_component`` - Renders a client-side PyScript component.
    * ``pyscript_setup`` - Renders PyScript setup configuration.

    Unlike Django's template tags, which require ``{% load reactpy %}`` and use
    ``{% component %}`` syntax, Jinja2 uses ``{{ component(...) }}`` function calls.
    This is because Jinja2 has more expressive power and can directly handle
    function expansions.
    """

    def __init__(self, environment):
        super().__init__(environment)
        environment.globals["component"] = self._component
        environment.globals["pyscript_component"] = self._pyscript_component
        environment.globals["pyscript_setup"] = self._pyscript_setup

    @pass_context
    def _component(
        self,
        jinja_context: Context,
        dotted_path: str,
        *args,
        host: str | None = None,
        prerender: str = "",
        offline: str = "",
        **kwargs,
    ) -> str:
        """Render a server-side ReactPy component.

        This is the Jinja2 equivalent of ``{% component "path.to.Component" %}``.

        Args:
            dotted_path: The dotted path to the component to render.
            *args: Positional arguments to pass to the component.
            host: The host to use for ReactPy connections.
            prerender: If ``"true"`` the component will be pre-rendered server-side.
            offline: Dotted path to an offline fallback component.
            **kwargs: Keyword arguments to pass to the component.

        Returns:
            Rendered HTML string.
        """
        request = jinja_context.parent.get("request")
        if request is None:
            _logger.error(
                "Cannot render a ReactPy component in a Jinja2 template without a "
                "request object. Ensure the 'django.template.context_processors.request' "
                "context processor is enabled for your Jinja2 backend."
            )
            return ""

        django_context = RequestContext(
            request,
            autoescape=jinja_context.eval_ctx.autoescape,
        )
        template_context = django_component_tag(
            django_context,
            dotted_path,
            *args,
            host=host,
            prerender=prerender,
            offline=offline,
            **kwargs,
        )
        return loader.render_to_string(
            COMPONENT_TEMPLATE,
            template_context,
            request,
        )

    @pass_context
    def _pyscript_component(
        self,
        jinja_context: Context,
        *file_paths: str,
        initial: str | VdomDict | Component = "",
        root: str = "root",
    ) -> str:
        """Render a client-side PyScript component.

        This is the Jinja2 equivalent of ``{% pyscript_component "path/to/file.py" %}``.

        Args:
            file_paths: File paths to client-side component Python files.
            initial: Initial HTML displayed before the PyScript component loads.
            root: The name of the root component function.

        Returns:
            Rendered HTML string.
        """
        request = jinja_context.parent.get("request")
        if request is None:
            _logger.error("Cannot render a PyScript component in a Jinja2 template without a request object.")
            return ""

        django_context = RequestContext(
            request,
            autoescape=jinja_context.eval_ctx.autoescape,
        )
        template_context = django_pyscript_component_tag(
            django_context,
            *file_paths,
            initial=initial,
            root=root,
        )
        return loader.render_to_string(
            PYSCRIPT_COMPONENT_TEMPLATE,
            template_context,
            request,
        )

    def _pyscript_setup(
        self,
        *extra_py: str,
        extra_js: str | dict = "",
        config: str | dict = "",
    ) -> str:
        """Render PyScript setup configuration.

        This is the Jinja2 equivalent of ``{% pyscript_setup %}``.

        Args:
            extra_py: Additional Python dependencies.
            extra_js: Additional JavaScript modules.
            config: PyScript configuration overrides.

        Returns:
            Rendered HTML string.
        """
        template_context = django_pyscript_setup_tag(
            *extra_py,
            extra_js=extra_js,
            config=config,
        )
        return loader.render_to_string(
            PYSCRIPT_SETUP_TEMPLATE,
            template_context,
        )
