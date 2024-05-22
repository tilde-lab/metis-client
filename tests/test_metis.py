"Test MetisAPI"

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from yarl import URL

from metis_client import MetisAPI, MetisNoAuth
from metis_client.exc import (
    MetisAsyncRuntimeWarning,
    MetisConnectionException,
    MetisException,
)


async def create_app() -> web.Application:
    "Create web application"
    app = web.Application()
    return app


@pytest.fixture
async def aiohttp_client(aiohttp_client) -> TestClient:
    "Create test client"
    app = await create_app()
    return await aiohttp_client(TestServer(app))


@pytest.fixture
def base_url(aiohttp_client: TestClient) -> URL:
    "Return base url"
    return aiohttp_client.make_url("")


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
async def test_sync_ns_timeout(base_url: URL, default_timeout, timeout, result):
    "Test timeout guessing method"
    client = MetisAPI(base_url, auth=MetisNoAuth(), timeout=default_timeout)
    # pylint: disable=protected-access
    assert client.v0._get_timeout(timeout) == result


async def test_sync_in_async_runtime(base_url: URL):
    """
    Use sync API in an async runtime.
    It's impossible to connect to the test fake server
    because of runtime block by synchronous function call.
    So, we check that:
     - RuntimeError is absent (asyncio.run() cannot be called from a running event loop)
     - MetisAsyncRuntimeWarning is present about misuse of API
     - timeout exception is present
    """
    client = MetisAPI(base_url, auth=MetisNoAuth(), timeout=0.0001)
    with pytest.warns(MetisAsyncRuntimeWarning):
        with pytest.raises((MetisConnectionException, MetisException)):  # noqa: B908
            client.v0.auth.whoami()
