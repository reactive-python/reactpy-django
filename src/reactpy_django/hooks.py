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
)
from uuid import uuid4

import orjson
from channels import DEFAULT_CHANNEL_LAYER
from channels.db import database_sync_to_async
from channels.layers import InMemoryChannelLayer, get_channel_layer
from reactpy import use_callback, use_effect, use_memo, use_ref, use_state
from reactpy import use_connection as _use_connection
from reactpy import use_location as _use_location
from reactpy import use_scope as _use_scope
from reactpy.backend.types import Location

from reactpy_django.exceptions import UserNotFoundError
from reactpy_django.types import (
    AsyncMessageReceiver,
    AsyncMessageSender,
    AsyncPostprocessor,
    ConnectionType,
    FuncParams,
    Inferred,
    Mutation,
    Query,
    SyncPostprocessor,
    UserData,
)
from reactpy_django.utils import django_query_postprocessor, generate_obj_name, get_pk

if TYPE_CHECKING:
    from channels_redis.core import RedisChannelLayer
    from django.contrib.auth.models import AbstractUser


_logger = logging.getLogger(__name__)
_REFETCH_CALLBACKS: DefaultDict[Callable[..., Any], set[Callable[[], None]]] = (
    DefaultDict(set)
)


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


def use_scope() -> dict[str, Any]:
    """Get the current ASGI scope dictionary"""
    scope = _use_scope()

    if isinstance(scope, dict):
        return scope

    raise TypeError(f"Expected scope to be a dict, got {type(scope)}")


def use_connection() -> ConnectionType:
    """Get the current `Connection` object"""
    return _use_connection()


def use_query(
    query: Callable[FuncParams, Awaitable[Inferred]] | Callable[FuncParams, Inferred],
    kwargs: dict[str, Any] | None = None,
    *,
    thread_sensitive: bool = True,
    postprocessor: (
        AsyncPostprocessor | SyncPostprocessor | None
    ) = django_query_postprocessor,
    postprocessor_kwargs: dict[str, Any] | None = None,
) -> Query[Inferred]:
    """This hook is used to execute functions in the background and return the result, \
        typically to read data the Django ORM.

    Args:
        query: A function that executes a query and returns some data.

    Kwargs:
        kwargs: Keyword arguments to passed into the `query` function.
        thread_sensitive: Whether to run the query in thread sensitive mode. \
            This mode only applies to sync query functions, and is turned on by default \
            due to Django ORM limitations.
        postprocessor: A callable that processes the query `data` before it is returned. \
            The first argument of postprocessor function must be the query `data`. All \
            proceeding arguments are optional `postprocessor_kwargs`. This postprocessor \
            function must return the modified `data`. \
            \
            If unset, `REACTPY_DEFAULT_QUERY_POSTPROCESSOR` is used. By default, this \
            is used to prevent Django's lazy query execution and supports `many_to_many` \
            and `many_to_one` as `postprocessor_kwargs`.
        postprocessor_kwargs: Keyworded arguments passed into the `postprocessor` function.

    Returns:
         An object containing `loading`/`#!python error` states, your `data` (if the query \
         has successfully executed), and a `refetch` callable that can be used to re-run the query.
    """

    should_execute, set_should_execute = use_state(True)
    data, set_data = use_state(cast(Inferred, None))
    loading, set_loading = use_state(True)
    error, set_error = use_state(cast(Union[Exception, None], None))
    query_ref = use_ref(query)
    kwargs = kwargs or {}
    postprocessor_kwargs = postprocessor_kwargs or {}

    if query_ref.current is not query:
        raise ValueError(f"Query function changed from {query_ref.current} to {query}.")

    async def execute_query() -> None:
        """The main running function for `use_query`"""
        try:
            # Run the query
            if asyncio.iscoroutinefunction(query):
                new_data = await query(**kwargs)
            else:
                new_data = await database_sync_to_async(
                    query, thread_sensitive=thread_sensitive
                )(**kwargs)

            # Run the postprocessor
            if postprocessor:
                if asyncio.iscoroutinefunction(postprocessor):
                    new_data = await postprocessor(new_data, **postprocessor_kwargs)
                else:
                    new_data = await database_sync_to_async(
                        postprocessor, thread_sensitive=thread_sensitive
                    )(new_data, **postprocessor_kwargs)

        # Log any errors and set the error state
        except Exception as e:
            set_data(cast(Inferred, None))
            set_loading(False)
            set_error(e)
            _logger.exception("Failed to execute query: %s", generate_obj_name(query))
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

    # Return Query user API
    return Query(data, loading, error, refetch)


def use_mutation(
    mutation: (
        Callable[FuncParams, bool | None] | Callable[FuncParams, Awaitable[bool | None]]
    ),
    *,
    thread_sensitive: bool = True,
    refetch: Callable[..., Any] | Sequence[Callable[..., Any]] | None = None,
) -> Mutation[FuncParams]:
    """This hook is used to modify data in the background, typically to create/update/delete \
    data from the Django ORM.
        
    Mutation functions can `return False` to prevent executing your `refetch` function. All \
    other returns are ignored. Mutation functions can be sync or async.

    Args:
        mutation: A callable that performs Django ORM create, update, or delete \
            functionality. If this function returns `False`, then your `refetch` \
            function will not be used.

    Kwargs:
        thread_sensitive: Whether to run the mutation in thread sensitive mode. \
            This mode only applies to sync mutation functions, and is turned on by default \
            due to Django ORM limitations.
        refetch:  A query function (the function you provide to your `use_query` \
            hook) or a sequence of query functions that need a `refetch` if the \
            mutation succeeds. This is useful for refreshing data after a mutation \
            has been performed.

    Returns:
        An object containing `#!python loading`/`#!python error` states, and a \
        `#!python reset` callable that will set `#!python loading`/`#!python error` \
        states to defaults. This object can be called to run the query.
    """

    loading, set_loading = use_state(False)
    error, set_error = use_state(cast(Union[Exception, None], None))

    # The main "running" function for `use_mutation`
    async def execute_mutation(exec_args, exec_kwargs) -> None:
        # Run the mutation
        try:
            if asyncio.iscoroutinefunction(mutation):
                should_refetch = await mutation(*exec_args, **exec_kwargs)
            else:
                should_refetch = await database_sync_to_async(
                    mutation, thread_sensitive=thread_sensitive
                )(*exec_args, **exec_kwargs)

        # Log any errors and set the error state
        except Exception as e:
            set_loading(False)
            set_error(e)
            _logger.exception(
                "Failed to execute mutation: %s", generate_obj_name(mutation)
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

    # Return mutation user API
    return Mutation(schedule_mutation, loading, error, reset)


def use_user() -> AbstractUser:
    """Get the current `User` object from either the WebSocket or HTTP request."""
    connection = use_connection()
    user = connection.scope.get("user") or getattr(connection.carrier, "user", None)
    if user is None:
        raise UserNotFoundError("No user is available in the current environment.")
    return user


def use_user_data(
    default_data: (
        None | dict[str, Callable[[], Any] | Callable[[], Awaitable[Any]] | Any]
    ) = None,
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

        pk = get_pk(user)
        model, _ = await UserDataModel.objects.aget_or_create(user_pk=pk)
        model.data = orjson.dumps(data)
        await model.asave()

    query: Query[dict | None] = use_query(
        _get_user_data,
        kwargs={
            "user": user,
            "default_data": default_data,
            "save_default_data": save_default_data,
        },
        postprocessor=None,
    )
    mutation = use_mutation(_set_user_data, refetch=_get_user_data)

    return UserData(query, mutation)


def use_channel_layer(
    name: str | None = None,
    *,
    group_name: str | None = None,
    group_add: bool = True,
    group_discard: bool = True,
    receiver: AsyncMessageReceiver | None = None,
    layer: str = DEFAULT_CHANNEL_LAYER,
) -> AsyncMessageSender:
    """
    Subscribe to a Django Channels layer to send/receive messages.

    Args:
        name: The name of the channel to subscribe to. If you define a `group_name`, you \
            can keep `name` undefined to auto-generate a unique name.
        group_name: If configured, any messages sent within this hook will be broadcasted \
            to all channels in this group.
        group_add: If `True`, the channel will automatically be added to the group \
            when the component mounts.
        group_discard: If `True`, the channel will automatically be removed from the \
            group when the component dismounts.
        receiver: An async function that receives a `message: dict` from a channel. \
            If more than one receiver waits on the same channel name, a random receiver \
            will get the result.
        layer: The channel layer to use. This layer must be defined in \
            `settings.py:CHANNEL_LAYERS`.
    """
    channel_layer: InMemoryChannelLayer | RedisChannelLayer = get_channel_layer(layer)
    channel_name = use_memo(lambda: str(name or uuid4()))

    if not name and not group_name:
        raise ValueError("You must define a `name` or `group_name` for the channel.")

    if not channel_layer:
        raise ValueError(
            f"Channel layer '{layer}' is not available. Are you sure you"
            " configured settings.py:CHANNEL_LAYERS properly?"
        )

    # Add/remove a group's channel during component mount/dismount respectively.
    @use_effect(dependencies=[])
    async def group_manager():
        if group_name and group_add:
            await channel_layer.group_add(group_name, channel_name)

        if group_name and group_discard:
            return lambda: asyncio.run(
                channel_layer.group_discard(group_name, channel_name)
            )

    # Listen for messages on the channel using the provided `receiver` function.
    @use_effect
    async def message_receiver():
        if not receiver:
            return

        while True:
            message = await channel_layer.receive(channel_name)
            await receiver(message)

    # User interface for sending messages to the channel
    async def message_sender(message: dict):
        if group_name:
            await channel_layer.group_send(group_name, message)
        else:
            await channel_layer.send(channel_name, message)

    return message_sender


def use_root_id() -> str:
    """Get the root element's ID. This value is guaranteed to be unique. Current versions of \
        ReactPy-Django return a `uuid4` string."""
    scope = use_scope()

    return scope["reactpy"]["id"]


async def _get_user_data(
    user: AbstractUser, default_data: None | dict, save_default_data: bool
) -> dict | None:
    """The mutation function for `use_user_data`"""
    from reactpy_django.models import UserDataModel

    if not user or user.is_anonymous:
        return None

    pk = get_pk(user)
    model, _ = await UserDataModel.objects.aget_or_create(user_pk=pk)
    data = orjson.loads(model.data) if model.data else {}

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
            model.data = orjson.dumps(data)
            if save_default_data:
                await model.asave()

    return data
