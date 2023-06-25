"Test MetisCalculationsNamespace"

import asyncio
from datetime import datetime

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from aiohttp.web_exceptions import HTTPOk
from yarl import URL

from metis_client import MetisAPI, MetisAPIAsync, MetisTokenAuth
from tests.helpers import random_word

dt = datetime.fromordinal(1)
TOKEN = random_word(10)
PATH_C_ENGINES = "/calculations/supported"
PATH_C_GET_ENGINES_RESPONSE = ["dummy", "other", "results"]


async def get_engines_handler(_: web.Request) -> web.Response:
    "Request handler"
    return web.json_response(PATH_C_GET_ENGINES_RESPONSE, status=HTTPOk.status_code)


async def create_app() -> web.Application:
    "Create web application"
    app = web.Application()
    app.router.add_get(PATH_C_ENGINES, get_engines_handler)
    return app


@pytest.fixture
async def aiohttp_client_impl(aiohttp_client) -> TestClient:
    "Create test client"
    app = await create_app()
    return await aiohttp_client(TestServer(app))


@pytest.fixture
def base_url(aiohttp_client_impl: TestClient) -> URL:
    "Return base url"
    return aiohttp_client_impl.make_url("")


@pytest.fixture
def client(base_url: URL) -> MetisAPI:
    "Return sync client"
    return MetisAPI(base_url, auth=MetisTokenAuth(TOKEN))


@pytest.fixture
async def client_async(base_url: URL):
    "Return sync client"
    async with MetisAPIAsync(base_url, auth=MetisTokenAuth(TOKEN)) as client:
        yield client


async def test_get_supported(client: MetisAPI, client_async: MetisAPIAsync):
    "Test get_engines()"
    en_async = await client_async.calculations.supported()
    en_sync = await asyncio.get_event_loop().run_in_executor(
        None, client.calculations.supported
    )
    assert en_async == en_sync, "Response matches"
