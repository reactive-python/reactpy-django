from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Generic, Iterable, Optional, TypeVar, Union

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
    view: Union[View, Callable]
    args: Iterable
    kwargs: dict
