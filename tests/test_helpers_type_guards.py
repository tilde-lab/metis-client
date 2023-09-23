"Test type guards"

import pytest

from metis_client.dtos import (
    MetisErrorDTO,
    MetisErrorMessageDTO,
    MetisErrorEventDataDTO,
    MetisErrorEventDTO,
)
from metis_client.helpers import (
    is_metis_error_dto,
    is_metis_error_error_dto,
    is_metis_error_event_data_dto,
    is_metis_errors_evt_dto,
)

GOOD_ERROR_MSG: MetisErrorMessageDTO = {"message": "message"}
BAD_ERROR_MSG1 = "error error"
BAD_ERROR_MSG2 = {}
BAD_ERROR_MSG3 = {"message": None}


@pytest.mark.parametrize(
    "x,expected",
    [
        (GOOD_ERROR_MSG, True),
        (BAD_ERROR_MSG1, False),
        (BAD_ERROR_MSG2, False),
        (BAD_ERROR_MSG3, False),
    ],
)
def test_is_metis_error_error_dto(x, expected):
    "Test is_metis_error_error_dto"
    assert is_metis_error_error_dto(x) == expected


GOOD_ERROR1: MetisErrorDTO = {"status": 1, "error": "error message"}
GOOD_ERROR2: MetisErrorDTO = {"status": 1, "error": GOOD_ERROR_MSG}
BAD_ERROR1 = "error"
BAD_ERROR2 = {"status": 1}
BAD_ERROR3 = {"error": GOOD_ERROR_MSG}
BAD_ERROR4 = {"status": 1, "error": BAD_ERROR_MSG2}
IS_METIS_ERROR_DTO_PAMAMS = [
    (GOOD_ERROR1, True),
    (GOOD_ERROR2, True),
    (BAD_ERROR1, False),
    (BAD_ERROR2, False),
    (BAD_ERROR3, False),
    (BAD_ERROR4, False),
]


@pytest.mark.parametrize("x,expected", IS_METIS_ERROR_DTO_PAMAMS)
def test_is_metis_error_dto(x, expected):
    "Test is_metis_error_dto"
    assert is_metis_error_dto(x) == expected


GOOD_ERROR_EVENT_DATA1: MetisErrorEventDataDTO = {
    "reqId": "id",
    "data": [GOOD_ERROR1, GOOD_ERROR2],
}
GOOD_ERROR_EVENT_DATA2: MetisErrorEventDataDTO = {"reqId": "id", "data": []}
BAD_ERROR_EVENT_DATA1 = "error event data"
BAD_ERROR_EVENT_DATA2 = {}
BAD_ERROR_EVENT_DATA3 = {"reqId": "id"}
BAD_ERROR_EVENT_DATA4 = {"data": []}
BAD_ERROR_EVENT_DATA5 = {"reqId": "id", "data": ""}
BAD_ERROR_EVENT_DATA6 = {"reqId": "id", "data": [BAD_ERROR1]}
BAD_ERROR_EVENT_DATA7 = {"reqId": "id", "data": [GOOD_ERROR1, BAD_ERROR1]}


@pytest.mark.parametrize(
    "x,expected",
    [
        (GOOD_ERROR_EVENT_DATA1, True),
        (GOOD_ERROR_EVENT_DATA2, True),
        (BAD_ERROR_EVENT_DATA1, False),
        (BAD_ERROR_EVENT_DATA2, False),
        (BAD_ERROR_EVENT_DATA3, False),
        (BAD_ERROR_EVENT_DATA4, False),
        (BAD_ERROR_EVENT_DATA5, False),
        (BAD_ERROR_EVENT_DATA6, False),
        (BAD_ERROR_EVENT_DATA7, False),
    ],
)
def test_is_metis_error_event_data_dto(x, expected):
    "Test is_metis_error_event_data_dto"
    assert is_metis_error_event_data_dto(x) == expected


GOOD_ERROR_EVENT1: MetisErrorEventDTO = {
    "type": "errors",
    "data": GOOD_ERROR_EVENT_DATA1,
}
BAD_ERROR_EVENT1 = "event"
BAD_ERROR_EVENT2 = {"type": "no"}
BAD_ERROR_EVENT3 = {"type": "errors"}
BAD_ERROR_EVENT4 = {"type": "errors", "data": "data"}
IS_METIS_ERRORS_EVT_DTO_PARAMS = [
    (GOOD_ERROR_EVENT1, True),
    (BAD_ERROR_EVENT1, False),
    (BAD_ERROR_EVENT2, False),
    (BAD_ERROR_EVENT3, False),
    (BAD_ERROR_EVENT4, False),
]


@pytest.mark.parametrize("x,expected", IS_METIS_ERRORS_EVT_DTO_PARAMS)
def test_is_metis_errors_evt_dto(x, expected):
    "Test is_metis_errors_evt_dto"
    assert is_metis_errors_evt_dto(x) == expected
