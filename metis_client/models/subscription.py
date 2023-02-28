"Stream subscription"
import sys
from asyncio import CancelledError, Queue, QueueFull
from contextlib import asynccontextmanager
from types import TracebackType
from typing import TYPE_CHECKING, Optional, Type

from ..dtos import MetisEventDTO, MetisRequestIdDTO
from ..helpers import raise_on_metis_error_in_event
from .base import MetisBase

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Awaitable, Callable
else:  # pragma: no cover
    from collections.abc import Awaitable, Callable

if TYPE_CHECKING:  # pragma: no cover
    from .hub import MetisHub

SubscribeCallable = Callable[[], "MetisSubscription"]
RequestIdCallable = Callable[[], Awaitable[MetisRequestIdDTO]]


@raise_on_metis_error_in_event
async def act_and_get_result_from_stream(
    sub_func: SubscribeCallable, func: RequestIdCallable
) -> MetisEventDTO:
    "Do a request and get response from stream"
    async with sub_func() as sub:
        resp = await func()
        async for msg in sub:
            data = msg.get("data")
            if isinstance(data, dict) and data.get("reqId") == resp.get("reqId"):
                return msg
    raise CancelledError  # pragma: no cover


class MetisSubscription(MetisBase):
    "Message subscription"
    hub: "MetisHub"
    queue: "Queue[MetisEventDTO]"

    def __init__(
        self,
        hub: "MetisHub",
        predicate: Optional[Callable[[MetisEventDTO], bool]] = None,
        queue_size: int = 0,
    ) -> None:
        self.hub = hub
        self.queue = Queue(maxsize=queue_size)
        self._predicate = predicate

    def put_nowait(self, message: MetisEventDTO) -> None:
        "Put message to query without wait"
        try:
            if self._predicate is None or self._predicate(message):
                self.queue.put_nowait(message)
        except QueueFull:
            self.logger.warning("Subscription's queue is full")

    async def close(self) -> None:
        "Close subscription and join message queue"
        self.hub.unsubscribe(self)
        await self.queue.join()

    def __len__(self) -> int:
        return self.queue.qsize()

    async def __aenter__(self) -> "MetisSubscription":
        self.hub.subscribe(self)
        await self.hub.wait_connected()
        return self.__aiter__()

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.hub.unsubscribe(self)

    def __aiter__(self) -> "MetisSubscription":
        return self

    @asynccontextmanager
    async def _cm(self):
        try:
            yield await self.queue.get()
        finally:
            self.queue.task_done()

    async def __anext__(self) -> MetisEventDTO:
        async with self._cm() as msg:
            return msg
