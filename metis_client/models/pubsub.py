from asyncio import Event, Queue, QueueFull
from contextlib import asynccontextmanager, suppress
from types import TracebackType
from typing import Callable, Set, Type

from aiohttp_sse_client.client import MessageEvent
from .base import MetisBase
from ..const import GenericType
from ..models.event import (
    MetisDatasourcesEvent,
    MetisCalculationsEvent,
    MetisEvents,
    MetisPongEvent,
    MetisErrorEvent,
    MetisOtherEvent,
)


def cast_event(evt: MessageEvent) -> MetisEvents:
    for cls in [
        MetisErrorEvent,
        MetisPongEvent,
        MetisDatasourcesEvent,
        MetisCalculationsEvent,
    ]:
        with suppress(TypeError):
            return cls.from_message_event(evt)
    return MetisOtherEvent.from_message_event(evt)


class MetisHub(MetisBase):
    _subscriptions: "Set[MetisSubscription]"

    def __init__(self) -> None:
        self._subscriptions = set()
        self._connected_event = Event()

    def __len__(self) -> int:
        return len(self._subscriptions)

    @property
    def connected(self) -> bool:
        return self._connected_event.is_set()

    def set_connected(self) -> None:
        self._connected_event.set()

    def set_disconnected(self) -> None:
        self._connected_event.clear()

    async def wait_connected(self) -> None:
        await self._connected_event.wait()

    def subscribe(self, subscription: "MetisSubscription") -> None:
        self._subscriptions.add(subscription)

    def unsubscribe(self, subscription: "MetisSubscription") -> None:
        self._subscriptions.discard(subscription)

    def unsubscribe_all(self) -> None:
        self._subscriptions.clear()

    async def close(self) -> None:
        subs = [item for item in self._subscriptions]
        self.unsubscribe_all()
        for sub in subs:
            await sub.close()

    def publish(self, message: MessageEvent) -> None:
        evt = cast_event(message)
        for sub in self._subscriptions:
            sub.put_nowait(evt)


class MetisSubscription(MetisBase):
    hub: "MetisHub"
    queue: Queue[MetisEvents]

    def __init__(
        self,
        hub: "MetisHub",
        predicate: Callable[[MetisEvents], bool] | None = None,
        queue_size: int = 0,
    ) -> None:
        self.hub = hub
        self.queue = Queue(maxsize=queue_size)
        self._predicate = predicate

    def put_nowait(self, message: MetisEvents) -> None:
        try:
            if self._predicate is None or self._predicate(message):
                self.queue.put_nowait(message)
        except QueueFull:
            self.logger.warning("Subscription's queue is full")

    async def close(self) -> None:
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
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
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

    async def __anext__(self) -> MetisEvents:
        async with self._cm() as msg:
            return msg
