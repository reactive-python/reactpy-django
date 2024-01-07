from __future__ import annotations

import asyncio
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    DefaultDict,
    Sequence,
    Union,
    cast,
    overload,
)

import orjson as pickle
from channels.db import database_sync_to_async
from reactpy import use_callback, use_effect, use_ref, use_state
from reactpy import use_connection as _use_connection
from reactpy import use_location as _use_location
from reactpy import use_scope as _use_scope
from reactpy.backend.types import Location

from reactpy_django.exceptions import UserNotFoundError
from reactpy_django.types import (
    ConnectionType,
    FuncParams,
    Inferred,
    Mutation,
    MutationOptions,
    Query,
    QueryOptions,
    UserData,
)
from reactpy_django.utils import generate_obj_name, get_user_pk

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


_logger = logging.getLogger(__name__)
_REFETCH_CALLBACKS: DefaultDict[
    Callable[..., Any], set[Callable[[], None]]
] = DefaultDict(set)


# TODO: Deprecate this once the equivalent hook gets moved to reactpy.hooks.*
def use_location() -> Location:
    """Get the current route as a `Location` object"""
    return _use_location()


def use_origin() -> str | None:
    """Get the current origin as a string. If the browser did not send an origin header,
    this will be None."""
    scope = _use_scope()
    try:
        if scope["type"] == "websocket":
            return next(
                (
                    header[1].decode("utf-8")
                    for header in scope["headers"]
                    if header[0] == b"origin"
                ),
                None,
            )
        if scope["type"] == "http":
            host = next(
                (
                    header[1].decode("utf-8")
                    for header in scope["headers"]
                    if header[0] == b"host"
                )
            )
            return f"{scope['scheme']}://{host}" if host else None
    except Exception:
        _logger.info("Failed to get origin")
    return None


# TODO: Deprecate this once the equivalent hook gets moved to reactpy.hooks.*
def use_scope() -> dict[str, Any]:
    """Get the current ASGI scope dictionary"""
    scope = _use_scope()

    if isinstance(scope, dict):
        return scope

    raise TypeError(f"Expected scope to be a dict, got {type(scope)}")


# TODO: Deprecate this once the equivalent hook gets moved to reactpy.hooks.*
def use_connection() -> ConnectionType:
    """Get the current `Connection` object"""
    return _use_connection()


@overload
def use_query(
    options: QueryOptions,
    /,
    query: Callable[FuncParams, Awaitable[Inferred]] | Callable[FuncParams, Inferred],
    *args: FuncParams.args,
    **kwargs: FuncParams.kwargs,
) -> Query[Inferred]:
    ...


@overload
def use_query(
    query: Callable[FuncParams, Awaitable[Inferred]] | Callable[FuncParams, Inferred],
    *args: FuncParams.args,
    **kwargs: FuncParams.kwargs,
) -> Query[Inferred]:
    ...


def use_query(*args, **kwargs) -> Query[Inferred]:
    """This hook is used to execute functions in the background and return the result, \
        typically to read data the Django ORM.

    Args:
        options: An optional `QueryOptions` object that can modify how the query is executed.
        query: A callable that returns a Django `Model` or `QuerySet`.
        *args: Positional arguments to pass into `query`.

    Keyword Args:
        **kwargs: Keyword arguments to pass into `query`."""

    should_execute, set_should_execute = use_state(True)
    data, set_data = use_state(cast(Inferred, None))
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

    async def execute_query() -> None:
        """The main running function for `use_query`"""
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
            set_data(cast(Inferred, None))
            set_loading(False)
            set_error(e)
            _logger.exception(f"Failed to execute query: {generate_obj_name(query)}")
            return

        # Query was successful
        else:
            set_data(new_data)
            set_loading(False)
            set_error(None)

    @use_effect(dependencies=None)
    def schedule_query() -> None:
        """Schedule the query to be run when needed"""
        # Make sure we don't re-execute the query unless we're told to
        if not should_execute:
            return
        set_should_execute(False)

        # Execute the query in the background
        asyncio.create_task(execute_query())

    @use_callback
    def refetch() -> None:
        """Callable provided to the user, used to re-execute the query"""
        set_should_execute(True)
        set_loading(True)
        set_error(None)

    @use_effect(dependencies=[])
    def register_refetch_callback() -> Callable[[], None]:
        """Track the refetch callback so we can re-execute the query"""
        # By tracking callbacks globally, any usage of the query function will be re-run
        # if the user has told a mutation to refetch it.
        _REFETCH_CALLBACKS[query].add(refetch)
        return lambda: _REFETCH_CALLBACKS[query].remove(refetch)

    # The query's user API
    return Query(data, loading, error, refetch)


@overload
def use_mutation(
    options: MutationOptions,
    mutation: Callable[FuncParams, bool | None]
    | Callable[FuncParams, Awaitable[bool | None]],
    refetch: Callable[..., Any] | Sequence[Callable[..., Any]] | None = None,
) -> Mutation[FuncParams]:
    ...


@overload
def use_mutation(
    mutation: Callable[FuncParams, bool | None]
    | Callable[FuncParams, Awaitable[bool | None]],
    refetch: Callable[..., Any] | Sequence[Callable[..., Any]] | None = None,
) -> Mutation[FuncParams]:
    ...


def use_mutation(*args: Any, **kwargs: Any) -> Mutation[FuncParams]:
    """This hook is used to modify data in the background, typically to create/update/delete \
    data from the Django ORM.
        
    Mutation functions can `return False` to prevent executing your `refetch` function. All \
    other returns are ignored. Mutation functions can be sync or async.

    Args:
        mutation: A callable that performs Django ORM create, update, or delete \
            functionality. If this function returns `False`, then your `refetch` \
            function will not be used.
        refetch:  A query function (the function you provide to your `use_query` \
            hook) or a sequence of query functions that need a `refetch` if the \
            mutation succeeds. This is useful for refreshing data after a mutation \
            has been performed.
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
                f"Failed to execute mutation: {generate_obj_name(mutation)}"
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
        *exec_args: FuncParams.args, **exec_kwargs: FuncParams.kwargs
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


def use_user() -> AbstractUser:
    """Get the current `User` object from either the WebSocket or HTTP request."""
    connection = use_connection()
    user = connection.scope.get("user") or getattr(connection.carrier, "user", None)
    if user is None:
        raise UserNotFoundError("No user is available in the current environment.")
    return user


def use_user_data(
    default_data: None
    | dict[str, Callable[[], Any] | Callable[[], Awaitable[Any]] | Any] = None,
    save_default_data: bool = False,
) -> UserData:
    """Get or set user data stored within the REACTPY_DATABASE.
    
    Kwargs:
        default_data: A dictionary containing `{key: default_value}` pairs. \
            For computationally intensive defaults, your `default_value` \
            can be sync or async functions that return the value to set.
        save_default_data: If True, `default_data` values will automatically be stored \
            within the database if they do not exist.
    """
    from reactpy_django.models import UserDataModel

    user = use_user()

    async def _set_user_data(data: dict):
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict while setting user data, got {type(data)}")
        if user.is_anonymous:
            raise ValueError("AnonymousUser cannot have user data.")

        pk = get_user_pk(user)
        model, _ = await UserDataModel.objects.aget_or_create(user_pk=pk)
        model.data = pickle.dumps(data)
        await model.asave()

    query: Query[dict | None] = use_query(
        QueryOptions(postprocessor=None),
        _get_user_data,
        user=user,
        default_data=default_data,
        save_default_data=save_default_data,
    )
    mutation = use_mutation(_set_user_data, refetch=_get_user_data)

    return UserData(query, mutation)


def _use_query_args_1(options: QueryOptions, /, query: Query, *args, **kwargs):
    return options, query, args, kwargs


def _use_query_args_2(query: Query, *args, **kwargs):
    return QueryOptions(), query, args, kwargs


def _use_mutation_args_1(options: MutationOptions, mutation: Mutation, refetch=None):
    return options, mutation, refetch


def _use_mutation_args_2(mutation, refetch=None):
    return MutationOptions(), mutation, refetch


async def _get_user_data(
    user: AbstractUser, default_data: None | dict, save_default_data: bool
) -> dict | None:
    """The mutation function for `use_user_data`"""
    from reactpy_django.models import UserDataModel

    if not user or user.is_anonymous:
        return None

    pk = get_user_pk(user)
    model, _ = await UserDataModel.objects.aget_or_create(user_pk=pk)
    data = pickle.loads(model.data) if model.data else {}

    if not isinstance(data, dict):
        raise TypeError(f"Expected dict while loading user data, got {type(data)}")

    # Set default values, if needed
    if default_data:
        changed = False
        for key, value in default_data.items():
            if key not in data:
                new_value: Any = value
                if asyncio.iscoroutinefunction(value):
                    new_value = await value()
                elif callable(value):
                    new_value = value()
                data[key] = new_value
                changed = True
        if changed:
            model.data = pickle.dumps(data)
            if save_default_data:
                await model.asave()

    return data
