"Test MetisLocalUserAuth"
from itertools import count
from json import JSONDecodeError

import pytest
from aiohttp import CookieJar, web
from aiohttp.test_utils import TestClient, TestServer
from aiohttp.web_exceptions import (
    HTTPBadRequest,
    HTTPOk,
    HTTPTooManyRequests,
    HTTPUnauthorized,
)
from freezegun import freeze_time

from metis_client import MetisLocalUserAuth
from tests.helpers import random_word

EMAIL = random_word(10)
PASSWORD = random_word(10)

AUTH_PATH = f"/{MetisLocalUserAuth._endpoint}"  # pylint: disable=protected-access

TOO_MANY_COUNTER = count(0)


async def handler(request: web.Request) -> web.Response:
    "Request handler"
    # bad request
    try:
        payload = await request.json()
        if "email" not in payload or "password" not in payload:
            raise TypeError
    except (JSONDecodeError, TypeError):
        resp = web.Response(
            body=HTTPBadRequest.status, status=HTTPBadRequest.status_code
        )
        resp.set_cookie("_sid", "session but bad")
        return resp

    # simulate too many requests on the first request
    if next(TOO_MANY_COUNTER) < 1:
        resp = web.Response(body="not ok", status=HTTPTooManyRequests.status_code)
        resp.set_cookie("_sid", "session but bad")
        return resp

    # bad credentials
    if payload.get("email") != EMAIL or payload.get("password") != PASSWORD:
        resp = web.Response(body="not ok", status=HTTPUnauthorized.status_code)
        resp.set_cookie("_sid", "session but bad")
        return resp

    # ok
    resp = web.Response(body="ok", status=HTTPOk.status_code)
    resp.set_cookie("_sid", "ok")
    return resp


async def create_app() -> web.Application:
    "Create web application"
    app = web.Application()
    app.router.add_post(AUTH_PATH, handler)
    return app


@pytest.fixture
async def cli(aiohttp_client) -> TestClient:
    "Create test client"
    jar = CookieJar(unsafe=True, treat_as_secure_origin="http://127.0.0.1")
    return await aiohttp_client(TestServer(await create_app()), cookie_jar=jar)


@freeze_time("1970-01-01", auto_tick_seconds=10)
async def test_auth_ok(cli: TestClient):
    "Test successful authentication"
    authenticator = MetisLocalUserAuth(EMAIL, PASSWORD)
    base_url = cli.make_url("")
    assert await authenticator.should_update(
        cli.session, base_url
    ), "Update is needed before authentication"
    assert await authenticator.authenticate(
        cli.session, base_url
    ), "Correct email-password pair should authenticate"
    assert (
        await authenticator.should_update(cli.session, base_url) is False
    ), "Update is not needed after authentication"


async def test_auth_not_ok(cli: TestClient):
    "Test unsuccessful authentication"
    authenticator = MetisLocalUserAuth(EMAIL, "")
    base_url = cli.make_url("")
    assert (
        await authenticator.authenticate(cli.session, base_url) is False
    ), "Incorrect email-password pair should fail to authenticate"
    assert await authenticator.should_update(
        cli.session, base_url
    ), "Update is needed after failed authentication"
