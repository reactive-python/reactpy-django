from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Generic, Optional, Sequence, TypeVar, Union

from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.views.generic import View
from typing_extensions import ParamSpec


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
    view_id: str


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


@dataclass
class QueryOptions:
    """Configuration options that can be provided to `use_query`."""

    postprocessor_options: dict[str, Any] = field(
        default_factory=lambda: {"many_to_many": False, "many_to_one": False}
    )
    """Configuration values usable by the `postprocessor`."""

    postprocessor: Callable[[QueryOptions], None] | None = None
    """A post processing callable that can read/modify the `QueryOptions` object. If unset, the default fetch
    handler is used to prevent lazy loading of Django fields."""
