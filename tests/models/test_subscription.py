"Test MetisSubscription"

import logging

from metis_client.dtos.event import MetisErrorEventDTO
from metis_client.models import MetisHub, MetisSubscription

TEST_EVENT: MetisErrorEventDTO = {
    "type": "errors",
    "data": {"reqId": "1", "data": [{"status": 1, "error": "oops"}]},
}


async def test_queue_full(caplog):
    "Test internal queue is full"
    hub = MetisHub()
    sub = MetisSubscription(hub, queue_size=1)
    sub.put_nowait(TEST_EVENT)
    with caplog.at_level(logging.WARNING):
        sub.put_nowait(TEST_EVENT)
    assert "queue" in caplog.text
    await hub.close()


async def test_len():
    "Test subscription length"
    hub = MetisHub()
    sub = MetisSubscription(hub, queue_size=1)
    sub.put_nowait(TEST_EVENT)
    assert len(sub) == 1, "Internal queue size match"
    await hub.close()
