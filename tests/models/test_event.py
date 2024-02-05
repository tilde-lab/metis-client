"""Test MetisMessageEvent"""

import json

from metis_client.models import MetisMessageEvent


def test_encoding_error():
    "Test encoding error in to_dto()"

    evt = MetisMessageEvent("errors", "message", "data", "origin", "last_event_id")
    result = evt.to_dto()

    assert (
        isinstance(result["data"], dict)
        and result["data"].get("data", [{}])[-1].get("status") == 400
    ), "Shoult return error event with status 400"


def test_to_snake_case_conversion():
    "Test convertion of internal data to snake case"
    data = {"data": [{"reqId": 213, "dataSources": [{"typeId": 123}]}]}
    expected = {"data": [{"req_id": 213, "data_sources": [{"type_id": 123}]}]}
    evt = MetisMessageEvent("datasources", "", json.dumps(data), "", "")
    result = evt.to_dto()

    assert result["data"] == expected
