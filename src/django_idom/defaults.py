from __future__ import annotations

from typing import Any, Callable

from django.conf import settings

from django_idom.utils import _import_dotted_path


_DEFAULT_QUERY_POSTPROCESSOR: Callable[..., Any] | None = _import_dotted_path(
    getattr(
        settings,
        "IDOM_DEFAULT_QUERY_POSTPROCESSOR",
        "django_idom.utils.django_query_postprocessor",
    )
)
