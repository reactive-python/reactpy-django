# Copyright © 2023 Innovatie Ltd. All rights reserved.
"""
Jinja support.
"""
from django.template import RequestContext, loader
from jinja2 import pass_context
from jinja2.ext import Extension
from jinja2.runtime import Context
from reactpy_django import config
from reactpy_django.templatetags.reactpy import component

#
# Point to our non-Django analogue.
#
DJT_TEMPLATE = "reactpy/component.html"


class ReactPyExtension(Extension):
    """
    Jinja has more expressive power than core Django's templates, and can
    directly handle expansions such as:

        {{ component(*args, **kwargs) }}
    """

    #
    # Therefore, there is no new tag to parse().
    #
    tags = {}

    def __init__(self, environment):
        super().__init__(environment)
        #
        # All we need is to add global "component" to the environment.
        #
        environment.globals["component"] = self.template_tag

    @pass_context
    def template_tag(
        self, jinja_context: Context, dotted_path: str, *args, **kwargs
    ) -> str:
        """
        This method is used to embed an existing ReactPy component into your
        Jinja2 template.

        Args:
            dotted_path: String of the fully qualified name of a component.
            *args: The positional arguments to provide to the component.

        Keyword Args:
            **kwargs: The keyword arguments to provide to the component.

        Returns:
            Whatever the components returns.
        """
        django_context = RequestContext(
            jinja_context.parent["request"],
            autoescape=jinja_context.eval_ctx.autoescape,
        )
        template_context = component(django_context, dotted_path, *args, **kwargs)
        #
        # TODO: can this be usefully cached?
        #
        return loader.render_to_string(
            DJT_TEMPLATE, template_context, jinja_context.parent["request"]
        )
