"Test MetisAPI"

import pytest

from metis_client import MetisAPI, MetisNoAuth


@pytest.mark.parametrize(
    "default_timeout, timeout, result",
    [
        (False, False, None),
        (False, None, None),
        (False, 1, 1),
        (None, False, None),
        (None, None, None),
        (None, 1, 1),
        (1, False, None),
        (1, None, 1),
        (1, 1, 1),
    ],
)
async def test_sync_ns_timeout(default_timeout, timeout, result):
    "Test timeout guessing method"
    client = MetisAPI("/", auth=MetisNoAuth(), timeout=default_timeout)
    # pylint: disable=protected-access
    assert client.v0._get_timeout(timeout) == result
