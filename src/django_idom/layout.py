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
        async_unsafe_prev = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE", None)

        # Set ALLOW ASYNC UNSAFE to True
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        layout_update = super()._create_layout_update(old_state)

        # Reset async unsafe flag to the previous value
        if async_unsafe_prev is not None:
            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = async_unsafe_prev
        else:
            os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE")

        return layout_update
