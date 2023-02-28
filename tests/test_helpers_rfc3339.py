"Test parse_rfc3339 helper"
from datetime import datetime, timedelta, timezone

import pytest

from metis_client.helpers import parse_rfc3339

expected_dt = datetime(2001, 2, 3, 4, 5, 6)
expected_dt_tz = expected_dt.replace(tzinfo=timezone.utc)
expected_dt_ms_tz = expected_dt_tz + timedelta(microseconds=789012)

testdata = [
    (None, None),
    ("", None),
    (expected_dt, expected_dt),
    ("2001-02-03 04:05:06Z", expected_dt_tz),
    ("2001-02-03T04:05:06Z", expected_dt_tz),
    ("2001-02-03 04:05:06.789012+00:00", expected_dt_ms_tz),
    ("2001-02-03T04:05:06.789012+00:00", expected_dt_ms_tz),
    ("2001-02-03 04:05:06+00:00", expected_dt_tz),
    ("2001-02-03T04:05:06+00:00", expected_dt_tz),
    ("2001-02-03 04:05:06", expected_dt),
    ("2001-02-03T04:05:06", expected_dt),
]


@pytest.mark.parametrize("x,expected", testdata)
def test_parse_rfc3339(x, expected):
    "Test parse_rfc3339"
    assert parse_rfc3339(x) == expected, "Value should be expected"
