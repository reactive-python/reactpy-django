from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import Any, Awaitable, Callable, DefaultDict, Sequence, Union, cast

from channels.db import database_sync_to_async as _database_sync_to_async
from django.db.models import ManyToManyField, prefetch_related_objects
from django.db.models.base import Model
from django.db.models.fields.reverse_related import ManyToOneRel
from django.db.models.query import QuerySet
from idom import use_callback, use_ref
from idom.backend.types import Location
from idom.core.hooks import Context, create_context, use_context, use_effect, use_state

from django_idom.types import IdomWebsocket, Mutation, OrmFetch, Query, _Params, _Result
from django_idom.utils import _generate_obj_name


_logger = logging.getLogger(__name__)
database_sync_to_async = cast(
    Callable[..., Callable[..., Awaitable[Any]]],
    _database_sync_to_async,
)
WebsocketContext: Context[IdomWebsocket | None] = create_context(None)
_REFETCH_CALLBACKS: DefaultDict[
    Callable[..., Any], set[Callable[[], None]]
] = DefaultDict(set)


def use_location() -> Location:
    """Get the current route as a `Location` object"""
    # TODO: Use the browser's current page, rather than the WS route
    scope = use_scope()
    search = scope["query_string"].decode()
    return Location(scope["path"], f"?{search}" if search else "")


def use_origin() -> str | None:
    """Get the current origin as a string. If the browser did not send an origin header,
    this will be None."""
    scope = use_scope()
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
    return use_websocket().scope


def use_websocket() -> IdomWebsocket:
    """Get the current IdomWebsocket object"""
    websocket = use_context(WebsocketContext)
    if websocket is None:
        raise RuntimeError("No websocket. Are you running with a Django server?")
    return websocket


def use_query(
    query: Callable[_Params, _Result | None] | OrmFetch,
    *args: _Params.args,
    **kwargs: _Params.kwargs,
) -> Query[_Result | None]:
    """Hook to fetch a Django ORM query.

    Args:
        query: A callable that returns a Django `Model` or `QuerySet`.
        *args: Positional arguments to pass into `query`.

    Keyword Args:
        **kwargs: Keyword arguments to pass into `query`."""
    query_ref = use_ref(query)
    if query_ref.current is not query:
        raise ValueError(f"Query function changed from {query_ref.current} to {query}.")

    should_execute, set_should_execute = use_state(True)
    data, set_data = use_state(cast(Union[_Result, None], None))
    loading, set_loading = use_state(True)
    error, set_error = use_state(cast(Union[Exception, None], None))
    fetch_cls = query if isinstance(query, OrmFetch) else OrmFetch(query)

    @use_callback
    def refetch() -> None:
        set_should_execute(True)
        set_loading(True)
        set_error(None)

    @use_effect(dependencies=[])
    def add_refetch_callback() -> Callable[[], None]:
        # By tracking callbacks globally, any usage of the query function will be re-run
        # if the user has told a mutation to refetch it.
        _REFETCH_CALLBACKS[fetch_cls.func].add(refetch)
        return lambda: _REFETCH_CALLBACKS[fetch_cls.func].remove(refetch)

    @use_effect(dependencies=None)
    @database_sync_to_async
    def execute_query() -> None:
        if not should_execute:
            return

        try:
            # Run the initial query
            fetch_cls.data = fetch_cls.func(*args, **kwargs)

            # Use a custom evaluator, if provided
            if fetch_cls.evaluator:
                fetch_cls.evaluator(fetch_cls)

            # Evaluate lazy Django fields
            else:
                _evaluate_django_query(fetch_cls)
        except Exception as e:
            set_data(None)
            set_loading(False)
            set_error(e)
            _logger.exception(
                f"Failed to execute query: {_generate_obj_name(query) or query}"
            )
            return
        finally:
            set_should_execute(False)

        set_data(fetch_cls.data)
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
                    f"Failed to execute mutation: {_generate_obj_name(mutate) or mutate}"
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


def _evaluate_django_query(fetch_cls: OrmFetch) -> None:
    """Recursively fetch all fields within a `Model` or `QuerySet` to ensure they are not performed lazily.

    Some behaviors can be modified through `OrmFetch` attributes."""
    data = fetch_cls.data

    # `QuerySet`, which is effectively a list of `Model` instances
    # https://github.com/typeddjango/django-stubs/issues/704
    if isinstance(data, QuerySet):  # type: ignore[misc]
        for model in data:
            _evaluate_django_query(
                OrmFetch(
                    func=fetch_cls.func,
                    data=model,
                    options=fetch_cls.options,
                )
            )

    # `Model` instances
    elif isinstance(data, Model):
        prefetch_fields = []
        for field in data._meta.get_fields():
            # `ForeignKey` relationships will cause an `AttributeError`
            # This is handled within the `ManyToOneRel` conditional below.
            with contextlib.suppress(AttributeError):
                getattr(data, field.name)

            if (
                fetch_cls.options.get("many_to_one", None)
                and type(field) == ManyToOneRel
            ):
                prefetch_fields.append(f"{field.name}_set")

            elif fetch_cls.options.get("many_to_many", None) and isinstance(
                field, ManyToManyField
            ):
                prefetch_fields.append(field.name)
                _evaluate_django_query(
                    OrmFetch(
                        func=fetch_cls.func,
                        data=getattr(data, field.name).get_queryset(),
                        options=fetch_cls.options,
                    )
                )

        if prefetch_fields:
            prefetch_related_objects([data], *prefetch_fields)

    # Unrecognized type
    else:
        raise ValueError(f"Expected a Model or QuerySet, got {data!r}")
