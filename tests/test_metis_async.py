"Test MetisAPIAsync"

import pytest

from metis_client import MetisAPIAsync, MetisNoAuth


async def test_relative_url():
    "Test relative url"
    with pytest.raises(TypeError):
        MetisAPIAsync("/relative", auth=MetisNoAuth())
