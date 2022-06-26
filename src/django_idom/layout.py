import os

from idom.core.layout import Layout, LayoutUpdate


class DjangoLayout(Layout):
    """Fixes Django ORM usage within components.
    These issues are caused by async/sync mixed context limitations in the ORM.
    Without this, `SynchronousOnlyOperation` exceptions occur when using the ORM in IDOM components.
    This may be fixed in a future version, such as Django 5.0."""

    def _create_layout_update(self, old_state) -> LayoutUpdate:
        """Create a layout update, but set ALLOW ASYNC UNSAFE flags prior.
        This allows the Django ORM to be used within components."""
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        layout_update = super()._create_layout_update(old_state)
        os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE")
        return layout_update
