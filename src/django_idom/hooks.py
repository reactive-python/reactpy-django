from __future__ import annotations

import asyncio
import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    DefaultDict,
    MutableMapping,
    Sequence,
    Union,
    cast,
    overload,
)

from channels.db import database_sync_to_async as _database_sync_to_async
from idom import use_callback, use_ref
from idom.backend.hooks import use_connection as _use_connection
from idom.backend.hooks import use_location as _use_location
from idom.backend.hooks import use_scope as _use_scope
from idom.backend.types import Location
from idom.core.hooks import use_effect, use_state

from django_idom.types import (
    Connection,
    Mutation,
    Query,
    QueryOptions,
    _Params,
    _Result,
)
from django_idom.utils import generate_obj_name


_logger = logging.getLogger(__name__)
database_sync_to_async = cast(
    Callable[..., Callable[..., Awaitable[Any]]],
    _database_sync_to_async,
)
_REFETCH_CALLBACKS: DefaultDict[
    Callable[..., Any], set[Callable[[], None]]
] = DefaultDict(set)


def use_location() -> Location:
    """Get the current route as a `Location` object"""
    return _use_location()


def use_origin() -> str | None:
    """Get the current origin as a string. If the browser did not send an origin header,
    this will be None."""
    scope = _use_scope()
    try:
        return next(
            (
                header[1].decode("utf-8")
                for header in scope["headers"]
                if header[0] == b"origin"
            ),
            None,
        )
    except Exception:
        return None


def use_scope() -> MutableMapping[str, Any]:
    """Get the current ASGI scope dictionary"""
    return _use_scope()


def use_connection() -> Connection:
    """Get the current `Connection` object"""
    return _use_connection()


@overload
def use_query(
    options: QueryOptions,
    query: Callable[_Params, _Result | None],
    /,
    *args: _Params.args,
    **kwargs: _Params.kwargs,
) -> Query[_Result | None]:
    ...


@overload
def use_query(
    query: Callable[_Params, _Result | None],
    /,
    *args: _Params.args,
    **kwargs: _Params.kwargs,
) -> Query[_Result | None]:
    ...


def use_query(
    *args: Any,
    **kwargs: Any,
) -> Query[_Result | None]:
    """Hook to fetch a Django ORM query.

    Args:
        options: An optional `QueryOptions` object that can modify how the query is executed.
        query: A callable that returns a Django `Model` or `QuerySet`.
        *args: Positional arguments to pass into `query`.

    Keyword Args:
        **kwargs: Keyword arguments to pass into `query`."""

    if isinstance(args[0], QueryOptions):
        query_options = args[0]
        query = args[1]
        args = args[2:]

    else:
        query_options = QueryOptions()
        query = args[0]
        args = args[1:]

    query_ref = use_ref(query)
    if query_ref.current is not query:
        raise ValueError(f"Query function changed from {query_ref.current} to {query}.")

    should_execute, set_should_execute = use_state(True)
    data, set_data = use_state(cast(Union[_Result, None], None))
    loading, set_loading = use_state(True)
    error, set_error = use_state(cast(Union[Exception, None], None))

    @use_callback
    def refetch() -> None:
        set_should_execute(True)
        set_loading(True)
        set_error(None)

    @use_effect(dependencies=[])
    def add_refetch_callback() -> Callable[[], None]:
        # By tracking callbacks globally, any usage of the query function will be re-run
        # if the user has told a mutation to refetch it.
        _REFETCH_CALLBACKS[query].add(refetch)
        return lambda: _REFETCH_CALLBACKS[query].remove(refetch)

    @use_effect(dependencies=None)
    @database_sync_to_async
    def execute_query() -> None:
        if not should_execute:
            return

        try:
            # Run the initial query
            new_data = query(*args, **kwargs)

            if query_options.postprocessor:
                new_data = query_options.postprocessor(
                    new_data, **query_options.postprocessor_kwargs
                )

        except Exception as e:
            set_data(None)
            set_loading(False)
            set_error(e)
            _logger.exception(
                f"Failed to execute query: {generate_obj_name(query) or query}"
            )
            return
        finally:
            set_should_execute(False)

        set_data(new_data)
        set_loading(False)
        set_error(None)

    return Query(data, loading, error, refetch)


def use_mutation(
    mutate: Callable[_Params, bool | None],
    refetch: Callable[..., Any] | Sequence[Callable[..., Any]] | None = None,
) -> Mutation[_Params]:
    """Hook to create, update, or delete Django ORM objects.

    Args:
        mutate: A callable that performs Django ORM create, update, or delete
            functionality. If this function returns `False`, then your `refetch`
            function will not be used.
        refetch: A `query` function (used by the `use_query` hook) or a sequence of `query`
            functions that will be called if the mutation succeeds. This is useful for
            refetching data after a mutation has been performed.
    """

    loading, set_loading = use_state(False)
    error, set_error = use_state(cast(Union[Exception, None], None))

    @use_callback
    def call(*args: _Params.args, **kwargs: _Params.kwargs) -> None:
        set_loading(True)

        @database_sync_to_async
        def execute_mutation() -> None:
            try:
                should_refetch = mutate(*args, **kwargs)
            except Exception as e:
                set_loading(False)
                set_error(e)
                _logger.exception(
                    f"Failed to execute mutation: {generate_obj_name(mutate) or mutate}"
                )
            else:
                set_loading(False)
                set_error(None)

                # `refetch` will execute unless explicitly told not to
                # or if `refetch` was not defined.
                if should_refetch is not False and refetch:
                    for query in (refetch,) if callable(refetch) else refetch:
                        for callback in _REFETCH_CALLBACKS.get(query) or ():
                            callback()

        asyncio.ensure_future(execute_mutation())

    @use_callback
    def reset() -> None:
        set_loading(False)
        set_error(None)

    return Mutation(call, loading, error, reset)
