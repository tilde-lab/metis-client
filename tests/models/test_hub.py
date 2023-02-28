"Test MetisHub"

from metis_client.models import MetisHub, MetisSubscription


async def test_close_hub():
    "Test close()"
    hub = MetisHub()
    hub.subscribe(MetisSubscription(hub))
    await hub.close()
