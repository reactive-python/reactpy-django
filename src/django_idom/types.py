from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
    Union,
)

from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.views.generic import View
from typing_extensions import ParamSpec

from django_idom.defaults import _DEFAULT_QUERY_POSTPROCESSOR


__all__ = ["_Result", "_Params", "_Data", "IdomWebsocket", "Query", "Mutation"]

_Result = TypeVar("_Result", bound=Union[Model, QuerySet[Any]])
_Params = ParamSpec("_Params")
_Data = TypeVar("_Data")


@dataclass
class IdomWebsocket:
    """Websocket returned by the `use_websocket` hook."""

    scope: dict
    close: Callable[[Optional[int]], Awaitable[None]]
    disconnect: Callable[[int], Awaitable[None]]
    dotted_path: str


@dataclass
class Query(Generic[_Data]):
    """Queries generated by the `use_query` hook."""

    data: _Data
    loading: bool
    error: Exception | None
    refetch: Callable[[], None]


@dataclass
class Mutation(Generic[_Params]):
    """Mutations generated by the `use_mutation` hook."""

    execute: Callable[_Params, None]
    loading: bool
    error: Exception | None
    reset: Callable[[], None]


@dataclass
class ViewComponentIframe:
    view: View | Callable
    args: Sequence
    kwargs: dict


class Postprocessor(Protocol):
    def __call__(self, data: Any) -> Any:
        ...


@dataclass
class QueryOptions:
    """Configuration options that can be provided to `use_query`."""

    postprocessor: Postprocessor | None = _DEFAULT_QUERY_POSTPROCESSOR
    """A callable that can modify the query `data` after the query has been executed.

    The first argument of postprocessor must be the query `data`. All proceeding arguments
    are optional `postprocessor_kwargs` (see below). This postprocessor function must return
    the modified `data`.

    If `None`, the default postprocessor is used.

    This default Django query postprocessor prevents Django's lazy query execution, and
    additionally can be configured via `postprocessor_kwargs` to recursively fetch
    `many_to_many` and `many_to_one` fields."""

    postprocessor_kwargs: dict[str, Any] = field(default_factory=lambda: {})
    """Keyworded arguments directly passed into the `postprocessor` for configuration."""


@dataclass
class ComponentParamData:
    """Container used for serializing component parameters.
    This dataclass is pickled & stored in the database, then unpickled when needed."""

    args: tuple
    kwargs: dict
