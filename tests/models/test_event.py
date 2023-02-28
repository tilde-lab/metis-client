"""Test MetisMessageEvent"""

# from metis_client.dtos import MetisMessageEvent
from metis_client.models import MetisMessageEvent


def test_encoding_error():
    "Test encoding error in to_dto()"

    evt = MetisMessageEvent("errors", "message", "data", "origin", "last_event_id")
    result = evt.to_dto()

    assert (
        isinstance(result["data"], dict)
        and result["data"].get("data", [{}])[-1].get("status") == 400
    ), "Shoult return error event with status 400"
