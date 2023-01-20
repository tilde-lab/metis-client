from asyncio import Event, Task, create_task, sleep
from typing import Callable

from aiohttp_sse_client.client import MessageEvent

from .base import BaseNamespace
from ..models.pubsub import MetisHub, MetisSubscription


class MetisStreamNamespace(BaseNamespace):
    _hub: MetisHub
    _stream_task: Task | None = None
    _subscribe_event: Event

    def __post_init__(self) -> None:
        self._hub = MetisHub()
        self._stream_task = create_task(self._stream_consumer())
        self._subscribe_event = Event()
        return super().__post_init__()

    async def _stream_consumer(self):
        sse_task: Task | None = None

        def on_open():
            self._hub.set_connected()

        def on_message(evt: MessageEvent):
            self._hub.set_connected()
            self._hub.publish(evt)
            # cancel streaming task if no subscribers
            if sse_task and len(self._hub) == 0:
                self._hub.set_disconnected()
                sse_task.cancel()

        while True:
            await self._subscribe_event.wait()
            if sse_task is None or sse_task.done():
                sse_task = create_task(
                    self._client.sse(self._base_url, on_message, on_open)
                )
            self._subscribe_event.clear()
            while not self._hub.connected:
                await sleep(0.1)
                await self._root.v0.ping()

    def close(self):
        if self._stream_task:
            self._stream_task.cancel()

    def subscribe(self, predicate: Callable[[MessageEvent], bool] | None = None):
        self._subscribe_event.set()
        return MetisSubscription(self._hub, predicate=predicate)
