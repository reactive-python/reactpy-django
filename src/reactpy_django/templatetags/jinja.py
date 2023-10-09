# Copyright © 2023 Innovatie Ltd. All rights reserved.
"""
Jinja support.
"""
import typing as t

from django.template import RequestContext, loader
from jinja2 import pass_context
from jinja2.ext import Extension
from jinja2.runtime import Context, Undefined

from .reactpy import component as djt_component
from .. import config


class ReactPyExtension(Extension):
    """
    Jinja has more expressive power than core Django's templates, and can
    directly handle expansions such as:

        {{ component(*args, **kwargs) }}
    """
    DJT_TEMPLATE = 'reactpy/component.html'
    #
    # Therefore, there is no new tag to parse().
    #
    tags = {}

    def __init__(self, environment):
        super().__init__(environment)
        #
        # All we need is to add global "component" to the environment.
        #
        environment.globals["component"] = self._jinja_component

    @pass_context
    def _jinja_component(self, __context: Context, dotted_path: str, *args: t.Any, host: str | None = None,
                         prerender: str = str(config.REACTPY_PRERENDER), **kwargs: t.Any) -> t.Union[t.Any, Undefined]:
        """
        This method is used to embed an existing ReactPy component into your
        Jinja2 template.

        Args:
            dotted_path: String of the fully qualified name of a component.
            *args: The positional arguments to provide to the component.

        Keyword Args:
            class: The HTML class to apply to the top-level component div.
            key: Force the component's root node to use a specific key value. \
                Using key within a template tag is effectively useless.
            host: The host to use for the ReactPy connections. If set to `None`, \
                the host will be automatically configured. \
                Example values include: `localhost:8000`, `example.com`, `example.com/subdir`
            prerender: Configures whether to pre-render this component, which \
                enables SEO compatibility and reduces perceived latency.
            **kwargs: The keyword arguments to provide to the component.

        Returns:
            Whatever the components returns.
        """
        djt_context = RequestContext(__context.parent['request'], autoescape=__context.eval_ctx.autoescape)
        context = djt_component(djt_context, dotted_path, *args, host=host, prerender=prerender, **kwargs)
        #
        # TODO: can this be usefully cached?
        #
        result = loader.render_to_string(self.DJT_TEMPLATE, context, __context.parent['request'])
        return result
