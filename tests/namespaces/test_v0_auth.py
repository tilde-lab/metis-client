"Test MetisV0AuthNamespace"

import asyncio
from copy import deepcopy
from datetime import datetime

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from aiohttp.web_exceptions import HTTPOk
from yarl import URL

from metis_client import MetisAPI, MetisAPIAsync, MetisTokenAuth
from metis_client.dtos import MetisUserDTO
from metis_client.dtos.auth import MetisAuthCredentialsRequestDTO
from metis_client.exc import MetisAuthenticationException
from tests.helpers import random_word

dt = datetime.fromordinal(1)
TOKEN = random_word(10)
PATH_AUTH = "/v0/auth"
PATH_AUTH_GET_PAYLOAD: MetisUserDTO = {
    "id": 1,
    "firstName": random_word(10),
    "lastName": random_word(10),
    "email": random_word(10),
    "emailVerified": True,
    "roleLabel": random_word(10),
    "roleSlug": random_word(10),
    "permissions": {},
    "provider": "",
    "createdAt": dt,
    "updatedAt": dt,
}
PATH_AUTH_POST_PAYLOAD: MetisAuthCredentialsRequestDTO = {
    "email": random_word(10),
    "password": random_word(10),
}


async def auth_whoami_handler(_: web.Request) -> web.Response:
    "Request handler"
    payload = {
        **deepcopy(PATH_AUTH_GET_PAYLOAD),
        "createdAt": PATH_AUTH_GET_PAYLOAD.get("createdAt", dt).isoformat(),
        "updatedAt": PATH_AUTH_GET_PAYLOAD.get("updatedAt", dt).isoformat(),
    }
    return web.json_response(payload, status=HTTPOk.status_code)


async def auth_login_handler(request: web.Request) -> web.Response:
    "Request handler"
    payload = await request.json()
    if payload == PATH_AUTH_POST_PAYLOAD:
        return web.Response(status=HTTPOk.status_code)
    return web.Response(status=web.HTTPUnauthorized.status_code)


async def create_app() -> web.Application:
    "Create web application"
    app = web.Application()
    app.router.add_get(PATH_AUTH, auth_whoami_handler)
    app.router.add_post(PATH_AUTH, auth_login_handler)
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


@pytest.fixture
def client(base_url: URL) -> MetisAPI:
    "Return sync client"
    return MetisAPI(base_url, auth=MetisTokenAuth(TOKEN))


@pytest.fixture
async def client_async(base_url: URL):
    "Return sync client"
    async with MetisAPIAsync(base_url, auth=MetisTokenAuth(TOKEN)) as client:
        yield client


async def test_whoami(client: MetisAPI, client_async: MetisAPIAsync):
    "Test whoami()"
    whoami_async = await client_async.v0.auth.whoami()
    whoami = await asyncio.get_event_loop().run_in_executor(None, client.v0.auth.whoami)
    assert whoami_async == whoami == PATH_AUTH_GET_PAYLOAD, "Response matches"


async def test_login_ok(client: MetisAPI, client_async: MetisAPIAsync):
    "Test login()"
    args = (PATH_AUTH_POST_PAYLOAD["email"], PATH_AUTH_POST_PAYLOAD["password"])
    auth_async = await client_async.v0.auth.login(*args)
    auth_sync = await asyncio.get_event_loop().run_in_executor(
        None, client.v0.auth.login, *args
    )
    assert auth_async is True, "Auth should be successful"
    assert auth_async == auth_sync, "Results should be the same"


async def test_login_fail(client: MetisAPI, client_async: MetisAPIAsync):
    "Test login()"
    args = (random_word(10), random_word(10))
    with pytest.raises(MetisAuthenticationException):
        await client_async.v0.auth.login(*args)
    with pytest.raises(MetisAuthenticationException):
        await asyncio.get_event_loop().run_in_executor(
            None, client.v0.auth.login, *args
        )
