from __future__ import annotations

from threading import Thread
from types import FunctionType
from typing import (
    Type,
    Union,
    Any,
    Callable,
    DefaultDict,
    Sequence,
    Type,
    Union,
    TypeVar,
    Generic,
    NamedTuple,
)

from django.db.models.base import Model
from django.db.models.query import QuerySet
from typing_extensions import ParamSpec
from idom import use_callback

from idom.backend.types import Location
from idom.core.hooks import Context, create_context, use_context, use_state, use_effect
from django_idom.utils import UNDEFINED

from django_idom.types import IdomWebsocket


WebsocketContext: Type[Context[Union[IdomWebsocket, None]]] = create_context(
    None, "WebSocketContext"
)


def use_location() -> Location:
    """Get the current route as a string"""
    # TODO: Use the browser's current page, rather than the WS route
    scope = use_scope()
    search = scope["query_string"].decode()
    return Location(scope["path"], f"?{search}" if search else "")


def use_scope() -> dict[str, Any]:
    """Get the current ASGI scope dictionary"""
    return use_websocket().scope


def use_websocket() -> IdomWebsocket:
    """Get the current IdomWebsocket object"""
    websocket = use_context(WebsocketContext)
    if websocket is None:
        raise RuntimeError("No websocket. Are you running with a Django server?")
    return websocket


_REFETCH_CALLBACKS: DefaultDict[FunctionType, set[Callable[[], None]]] = DefaultDict(
    set
)


_Data = TypeVar("_Data")
_Params = ParamSpec("_Params")


def use_query(
    query: Callable[_Params, _Data],
    *args: _Params.args,
    fetch_deferred_fields: bool = True,
    **kwargs: _Params.kwargs,
) -> Query[_Data]:
    given_query = query
    query, _ = use_state(given_query)
    if given_query is not query:
        raise ValueError(f"Query function changed from {query} to {given_query}.")

    data, set_data = use_state(UNDEFINED)
    loading, set_loading = use_state(True)
    error, set_error = use_state(None)

    @use_callback
    def refetch() -> None:
        set_data(UNDEFINED)
        set_loading(True)
        set_error(None)

    @use_effect(dependencies=[])
    def add_refetch_callback():
        # By tracking callbacks globally, any usage of the query function will be re-run
        # if the user has told a mutation to refetch it.
        _REFETCH_CALLBACKS[query].add(refetch)
        return lambda: _REFETCH_CALLBACKS[query].remove(refetch)

    @use_effect(dependencies=None)
    def execute_query():
        if data is not UNDEFINED:
            return

        def thread_target():
            try:
                query_result = query(*args, **kwargs)
            except Exception as e:
                set_data(UNDEFINED)
                set_loading(False)
                set_error(e)
                return

            if isinstance(query_result, QuerySet):
                if fetch_deferred_fields:
                    for model in query_result:
                        _fetch_deferred_fields(model)
                else:
                    # still force query set to execute
                    for _ in query_result:
                        pass
            elif isinstance(query_result, Model):
                if fetch_deferred_fields:
                    _fetch_deferred_fields(query_result)
            elif fetch_deferred_fields:
                raise ValueError(
                    f"Expected {query} to return Model or Query because "
                    f"{fetch_deferred_fields=}, got {query_result!r}"
                )

            set_data(query_result)
            set_loading(False)
            set_error(None)

        # We need to run this in a thread so we don't prevent rendering when loading.
        # I'm also hoping that Django is ok with this since this thread won't have an
        # active event loop.
        Thread(target=thread_target, daemon=True).start()

    return Query(data, loading, error, refetch)


class Query(NamedTuple, Generic[_Data]):
    data: _Data
    loading: bool
    error: Exception | None
    refetch: Callable[[], None]


def use_mutation(
    mutate: Callable[_Params, None],
    refetch: Callable[..., Any] | Sequence[Callable[..., Any]],
) -> Mutation[_Params]:
    loading, set_loading = use_state(True)
    error, set_error = use_state(None)

    @use_callback
    def call(*args: _Params.args, **kwargs: _Params.kwargs) -> None:
        set_loading(True)

        def thread_target():
            try:
                mutate(*args, **kwargs)
            except Exception as e:
                set_loading(False)
                set_error(e)
            else:
                set_loading(False)
                set_error(None)
                for query in (refetch,) if isinstance(refetch, Query) else refetch:
                    refetch_callback = _REFETCH_CALLBACKS.get(query)
                    if refetch_callback is not None:
                        refetch_callback()

        # We need to run this in a thread so we don't prevent rendering when loading.
        # I'm also hoping that Django is ok with this since this thread won't have an
        # active event loop.
        Thread(target=thread_target, daemon=True).start()

    @use_callback
    def reset() -> None:
        set_loading(False)
        set_error(None)

    return Query(call, loading, error, reset)


class Mutation(NamedTuple, Generic[_Params]):
    execute: Callable[_Params, None]
    loading: bool
    error: Exception | None
    reset: Callable[[], None]


_Model = TypeVar("_Model", bound=Model)


def _fetch_deferred_fields(model: _Model) -> _Model:
    for field in model.get_deferred_fields():
        value = getattr(model, field)
        if isinstance(value, Model):
            _fetch_deferred_fields(value)
