"Stream hub and subscriptions"

from asyncio import Event, Queue, QueueFull
from contextlib import asynccontextmanager
from types import TracebackType
from typing import Callable, Optional, Set, Type

from ..models.event import MetisEvent
from .base import MetisBase


class MetisHub(MetisBase):
    "Stream hub"
    _subscriptions: "Set[MetisSubscription]"

    def __init__(self) -> None:
        self._subscriptions = set()
        self._connected_event = Event()

    def __len__(self) -> int:
        return len(self._subscriptions)

    @property
    def connected(self) -> bool:
        "Check if connected event is set"
        return self._connected_event.is_set()

    def set_connected(self) -> None:
        "Set connected event"
        self._connected_event.set()

    def set_disconnected(self) -> None:
        "Clear connected event"
        self._connected_event.clear()

    async def wait_connected(self) -> None:
        "Wait connected event"
        await self._connected_event.wait()

    def subscribe(self, subscription: "MetisSubscription") -> None:
        "Register subscription"
        self._subscriptions.add(subscription)

    def unsubscribe(self, subscription: "MetisSubscription") -> None:
        "Unsubscribe subscription"
        self._subscriptions.discard(subscription)

    def unsubscribe_all(self) -> None:
        "Unsubscribe all subscriptions"
        self._subscriptions.clear()

    async def close(self) -> None:
        "Close all subscriptions"
        subs = list(self._subscriptions)
        self.unsubscribe_all()
        for sub in subs:
            await sub.close()

    def publish(self, evt: MetisEvent) -> None:
        "Publish message to subscriptions"
        for sub in self._subscriptions:
            sub.put_nowait(evt)


class MetisSubscription(MetisBase):
    "Message subscription"
    hub: "MetisHub"
    queue: "Queue[MetisEvent]"

    def __init__(
        self,
        hub: "MetisHub",
        predicate: Optional[Callable[[MetisEvent], bool]] = None,
        queue_size: int = 0,
    ) -> None:
        self.hub = hub
        self.queue = Queue(maxsize=queue_size)
        self._predicate = predicate

    def put_nowait(self, message: MetisEvent) -> None:
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

    async def __anext__(self) -> MetisEvent:
        async with self._cm() as msg:
            return msg
