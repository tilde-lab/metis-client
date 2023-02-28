"Test convert_dict_items_to_datetime helper"
from typing import Any, Dict

import pytest

from metis_client.helpers import convert_dict_items_to_datetime, parse_rfc3339

testdata = [
    ({"some": 123}, {"some": 123}),
    (
        {"date": "2001-02-03 04:05:06", "str": "str", "int": int},
        {"date": parse_rfc3339("2001-02-03 04:05:06"), "str": "str", "int": int},
    ),
    (
        {"date": "2001-02-03 04:05:06", "other_date": "2001-02-03T04:05:06Z"},
        {
            "date": parse_rfc3339("2001-02-03 04:05:06"),
            "other_date": parse_rfc3339("2001-02-03T04:05:06Z"),
        },
    ),
    ({"date": ""}, {"date": None}),
    ({"date": None}, {"date": None}),
]


@pytest.mark.parametrize("x,expected", testdata)
def test_convert(x: Dict[str, Any], expected):
    "Test convert_dict_items_to_datetime()"
    y = convert_dict_items_to_datetime(["date", "other_date"], x)
    assert isinstance(y, type(x)), "Types should match"
    assert y == expected, "Converted should match expected value"
