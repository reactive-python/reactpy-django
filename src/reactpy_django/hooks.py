from __future__ import annotations

import asyncio
import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    DefaultDict,
    Sequence,
    Union,
    cast,
    overload,
)

from channels.db import database_sync_to_async
from reactpy import use_callback, use_ref
from reactpy.backend.hooks import use_connection as _use_connection
from reactpy.backend.hooks import use_location as _use_location
from reactpy.backend.hooks import use_scope as _use_scope
from reactpy.backend.types import Location
from reactpy.core.hooks import use_effect, use_state

from reactpy_django.types import (
    Connection,
    Mutation,
    MutationOptions,
    Query,
    QueryOptions,
    _Params,
    _Result,
)
from reactpy_django.utils import generate_obj_name


_logger = logging.getLogger(__name__)
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


def use_scope() -> dict[str, Any]:
    """Get the current ASGI scope dictionary"""
    scope = _use_scope()

    if isinstance(scope, dict):
        return scope

    raise TypeError(f"Expected scope to be a dict, got {type(scope)}")


def use_connection() -> Connection:
    """Get the current `Connection` object"""
    return _use_connection()


@overload
def use_query(
    options: QueryOptions,
    /,
    query: Callable[_Params, _Result | None]
    | Callable[_Params, Awaitable[_Result | None]],
    *args: _Params.args,
    **kwargs: _Params.kwargs,
) -> Query[_Result | None]:
    ...


@overload
def use_query(
    query: Callable[_Params, _Result | None]
    | Callable[_Params, Awaitable[_Result | None]],
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

    should_execute, set_should_execute = use_state(True)
    data, set_data = use_state(cast(Union[_Result, None], None))
    loading, set_loading = use_state(True)
    error, set_error = use_state(cast(Union[Exception, None], None))
    if isinstance(args[0], QueryOptions):
        query_options, query, query_args, query_kwargs = _use_query_args_1(
            *args, **kwargs
        )
    else:
        query_options, query, query_args, query_kwargs = _use_query_args_2(
            *args, **kwargs
        )
    query_ref = use_ref(query)
    if query_ref.current is not query:
        raise ValueError(f"Query function changed from {query_ref.current} to {query}.")

    # The main "running" function for `use_query`
    async def execute_query() -> None:
        try:
            # Run the query
            if asyncio.iscoroutinefunction(query):
                new_data = await query(*query_args, **query_kwargs)
            else:
                new_data = await database_sync_to_async(
                    query,
                    thread_sensitive=query_options.thread_sensitive,
                )(*query_args, **query_kwargs)

            # Run the postprocessor
            if query_options.postprocessor:
                if asyncio.iscoroutinefunction(query_options.postprocessor):
                    new_data = await query_options.postprocessor(
                        new_data, **query_options.postprocessor_kwargs
                    )
                else:
                    new_data = await database_sync_to_async(
                        query_options.postprocessor,
                        thread_sensitive=query_options.thread_sensitive,
                    )(new_data, **query_options.postprocessor_kwargs)

        # Log any errors and set the error state
        except Exception as e:
            set_data(None)
            set_loading(False)
            set_error(e)
            _logger.exception(
                f"Failed to execute query: {generate_obj_name(query) or query}"
            )
            return

        # Query was successful
        else:
            set_data(new_data)
            set_loading(False)
            set_error(None)

    # Schedule the query to be run when needed
    @use_effect(dependencies=None)
    def schedule_query() -> None:
        # Make sure we don't re-execute the query unless we're told to
        if not should_execute:
            return
        set_should_execute(False)

        # Execute the query in the background
        asyncio.create_task(execute_query())

    # Used when the user has told us to refetch this query
    @use_callback
    def refetch() -> None:
        set_should_execute(True)
        set_loading(True)
        set_error(None)

    # Track the refetch callback so we can re-execute the query
    @use_effect(dependencies=[])
    def add_refetch_callback() -> Callable[[], None]:
        # By tracking callbacks globally, any usage of the query function will be re-run
        # if the user has told a mutation to refetch it.
        _REFETCH_CALLBACKS[query].add(refetch)
        return lambda: _REFETCH_CALLBACKS[query].remove(refetch)

    # The query's user API
    return Query(data, loading, error, refetch)


@overload
def use_mutation(
    options: MutationOptions,
    mutation: Callable[_Params, bool | None]
    | Callable[_Params, Awaitable[bool | None]],
    refetch: Callable[..., Any] | Sequence[Callable[..., Any]] | None = None,
) -> Mutation[_Params]:
    ...


@overload
def use_mutation(
    mutation: Callable[_Params, bool | None]
    | Callable[_Params, Awaitable[bool | None]],
    refetch: Callable[..., Any] | Sequence[Callable[..., Any]] | None = None,
) -> Mutation[_Params]:
    ...


def use_mutation(*args: Any, **kwargs: Any) -> Mutation[_Params]:
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
    if isinstance(args[0], MutationOptions):
        mutation_options, mutation, refetch = _use_mutation_args_1(*args, **kwargs)
    else:
        mutation_options, mutation, refetch = _use_mutation_args_2(*args, **kwargs)

    # The main "running" function for `use_mutation`
    async def execute_mutation(exec_args, exec_kwargs) -> None:
        # Run the mutation
        try:
            if asyncio.iscoroutinefunction(mutation):
                should_refetch = await mutation(*exec_args, **exec_kwargs)
            else:
                should_refetch = await database_sync_to_async(
                    mutation, thread_sensitive=mutation_options.thread_sensitive
                )(*exec_args, **exec_kwargs)

        # Log any errors and set the error state
        except Exception as e:
            set_loading(False)
            set_error(e)
            _logger.exception(
                f"Failed to execute mutation: {generate_obj_name(mutation) or mutation}"
            )

        # Mutation was successful
        else:
            set_loading(False)
            set_error(None)

            # `refetch` will execute unless explicitly told not to
            # or if `refetch` was not defined.
            if should_refetch is not False and refetch:
                for query in (refetch,) if callable(refetch) else refetch:
                    for callback in _REFETCH_CALLBACKS.get(query) or ():
                        callback()

    # Schedule the mutation to be run when needed
    @use_callback
    def schedule_mutation(
        *exec_args: _Params.args, **exec_kwargs: _Params.kwargs
    ) -> None:
        # Set the loading state.
        # It's okay to re-execute the mutation if we're told to. The user
        # can use the `loading` state to prevent this.
        set_loading(True)

        # Execute the mutation in the background
        asyncio.ensure_future(
            execute_mutation(exec_args=exec_args, exec_kwargs=exec_kwargs)
        )

    # Used when the user has told us to reset this mutation
    @use_callback
    def reset() -> None:
        set_loading(False)
        set_error(None)

    # The mutation's user API
    return Mutation(schedule_mutation, loading, error, reset)


def _use_query_args_1(
    options: QueryOptions,
    /,
    query: Callable[_Params, _Result | None]
    | Callable[_Params, Awaitable[_Result | None]],
    *args: _Params.args,
    **kwargs: _Params.kwargs,
):
    return options, query, args, kwargs


def _use_query_args_2(
    query: Callable[_Params, _Result | None]
    | Callable[_Params, Awaitable[_Result | None]],
    *args: _Params.args,
    **kwargs: _Params.kwargs,
):
    return QueryOptions(), query, args, kwargs


def _use_mutation_args_1(
    options: MutationOptions,
    mutation: Callable[_Params, bool | None]
    | Callable[_Params, Awaitable[bool | None]],
    refetch: Callable[..., Any] | Sequence[Callable[..., Any]] | None = None,
):
    return options, mutation, refetch


def _use_mutation_args_2(
    mutation: Callable[_Params, bool | None]
    | Callable[_Params, Awaitable[bool | None]],
    refetch: Callable[..., Any] | Sequence[Callable[..., Any]] | None = None,
):
    return MutationOptions(), mutation, refetch
