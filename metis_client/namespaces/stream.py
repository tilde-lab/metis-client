"""Stream endpoint namespace"""
import asyncio
import sys
from typing import Optional

from aiohttp_sse_client.client import MessageEvent

from ..dtos import MetisEventDTO
from ..models import MetisHub, MetisMessageEvent, MetisSubscription
from .base import BaseNamespace

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Callable
else:  # pragma: no cover
    from collections.abc import Callable


class MetisStreamNamespace(BaseNamespace):
    """Stream endpoints namespace"""

    _hub: MetisHub
    _stream_task: Optional[asyncio.Task] = None
    _sse_client_task: Optional[asyncio.Task] = None
    _subscribe_event: asyncio.Event

    def __post_init__(self) -> None:
        self._hub = MetisHub()
        self._stream_task = asyncio.create_task(
            self._stream_consumer(), name="StreamConsumerTask"
        )
        self._subscribe_event = asyncio.Event()
        return super().__post_init__()

    async def _stream_consumer(self):
        def on_open():
            self._hub.set_connected()

        def on_message(evt: MessageEvent):
            self._hub.set_connected()
            evt_dto = MetisMessageEvent.from_dto(evt).to_dto()
            self._hub.publish(evt_dto)
            # cancel streaming task if no subscribers
            if self._sse_client_task and len(self._hub) == 0:
                self._hub.set_disconnected()
                self._sse_client_task.cancel()

        while True:
            await self._subscribe_event.wait()
            if self._sse_client_task is None or self._sse_client_task.done():
                self._sse_client_task = asyncio.create_task(
                    self._client.sse(self._base_url, on_message, on_open),
                    name="SSEClientTask",
                )
            self._subscribe_event.clear()
            while not self._hub.connected:
                await asyncio.sleep(0.1)
                await self._root.v0.ping()

    def close(self):
        "Close background stream consumer"
        if self._stream_task:
            self._stream_task.cancel()

    def subscribe(self, predicate: Optional[Callable[[MetisEventDTO], bool]] = None):
        "Subscribe to stream"
        self._subscribe_event.set()
        return MetisSubscription(self._hub, predicate=predicate)
