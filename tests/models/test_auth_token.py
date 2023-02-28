"Test MetisTokenAuth"

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from metis_client import MetisTokenAuth
from tests.helpers import random_word

TOKEN = random_word(10)


@pytest.fixture
async def cli(aiohttp_client) -> TestClient:
    "Create test client"
    return await aiohttp_client(TestServer(web.Application()))


async def test_auth(cli: TestClient):
    "Test successful authentication"
    authenticator = MetisTokenAuth(TOKEN)
    base_url = cli.make_url("")
    assert await authenticator.should_update(
        cli.session, base_url
    ), "Update is needed before authentication"
    assert (
        cli.session.headers.get("Authorization") is None
    ), "There is no Authorization header before authenticate"
    assert await authenticator.authenticate(
        cli.session, base_url
    ), "Token authentication is sucessful"
    assert (
        cli.session.headers.get("Authorization") == f"Bearer {TOKEN}"
    ), "There is the Authorization header with Bearer after authenticate"
    assert await authenticator.should_update(
        cli.session, base_url
    ), "Update is needed after authentication"
