from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    MutableMapping,
    Protocol,
    Sequence,
    TypeVar,
    Union,
)

from django.http import HttpRequest
from reactpy.types import Connection
from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from reactpy_django.websocket.consumer import ReactpyAsyncWebsocketConsumer


FuncParams = ParamSpec("FuncParams")
Inferred = TypeVar("Inferred")
ConnectionType = Connection[Union["ReactpyAsyncWebsocketConsumer", HttpRequest]]


@dataclass
class Query(Generic[Inferred]):
    """Queries generated by the `use_query` hook."""

    data: Inferred
    loading: bool
    error: Exception | None
    refetch: Callable[[], None]


@dataclass
class Mutation(Generic[FuncParams]):
    """Mutations generated by the `use_mutation` hook."""

    execute: Callable[FuncParams, None]
    loading: bool
    error: Exception | None
    reset: Callable[[], None]


class AsyncPostprocessor(Protocol):
    async def __call__(self, data: Any) -> Any:
        ...


class SyncPostprocessor(Protocol):
    def __call__(self, data: Any) -> Any:
        ...


@dataclass
class QueryOptions:
    """Configuration options that can be provided to `use_query`."""

    from reactpy_django.config import REACTPY_DEFAULT_QUERY_POSTPROCESSOR

    postprocessor: AsyncPostprocessor | SyncPostprocessor | None = (
        REACTPY_DEFAULT_QUERY_POSTPROCESSOR
    )
    """A callable that can modify the query `data` after the query has been executed.

    The first argument of postprocessor must be the query `data`. All proceeding arguments
    are optional `postprocessor_kwargs` (see below). This postprocessor function must return
    the modified `data`.

    If unset, REACTPY_DEFAULT_QUERY_POSTPROCESSOR is used.

    ReactPy's default django_query_postprocessor prevents Django's lazy query execution, and
    additionally can be configured via `postprocessor_kwargs` to recursively fetch
    `many_to_many` and `many_to_one` fields."""

    postprocessor_kwargs: MutableMapping[str, Any] = field(default_factory=lambda: {})
    """Keyworded arguments directly passed into the `postprocessor` for configuration."""

    thread_sensitive: bool = True
    """Whether to run the query in thread-sensitive mode. This setting only applies to sync query functions."""


@dataclass
class MutationOptions:
    """Configuration options that can be provided to `use_mutation`."""

    thread_sensitive: bool = True
    """Whether to run the mutation in thread-sensitive mode. This setting only applies to sync mutation functions."""


@dataclass
class ComponentParams:
    """Container used for serializing component parameters.
    This dataclass is pickled & stored in the database, then unpickled when needed."""

    args: Sequence
    kwargs: MutableMapping[str, Any]


@dataclass
class UserData(Generic[Inferred]):
    data: Query[Inferred]
    set_data: Mutation[Inferred]
