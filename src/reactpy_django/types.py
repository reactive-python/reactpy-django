from __future__ import annotations

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    MutableMapping,
    NamedTuple,
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

    def __call__(self, *args: FuncParams.args, **kwargs: FuncParams.kwargs) -> None:
        """Execute the mutation."""
        self.execute(*args, **kwargs)


class AsyncPostprocessor(Protocol):
    async def __call__(self, data: Any) -> Any: ...


class SyncPostprocessor(Protocol):
    def __call__(self, data: Any) -> Any: ...


@dataclass
class ComponentParams:
    """Container used for serializing component parameters.
    This dataclass is pickled & stored in the database, then unpickled when needed."""

    args: Sequence
    kwargs: MutableMapping[str, Any]


class UserData(NamedTuple):
    query: Query[dict | None]
    mutation: Mutation[dict]


class AsyncMessageReceiver(Protocol):
    async def __call__(self, message: dict) -> None: ...


class AsyncMessageSender(Protocol):
    async def __call__(self, message: dict) -> None: ...
