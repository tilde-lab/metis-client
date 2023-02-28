"Test MetisNoAuth"
import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from metis_client import MetisNoAuth


@pytest.fixture
async def cli(aiohttp_client) -> TestClient:
    "Create test client"
    return await aiohttp_client(TestServer(web.Application()))


async def test_auth(cli: TestClient):
    "Test no authentication"
    authenticator = MetisNoAuth()
    base_url = cli.make_url("")
    assert (
        await authenticator.should_update(cli.session, base_url) is False
    ), "Update is not needed before authentication"
    assert await authenticator.authenticate(
        cli.session, base_url
    ), "Authenticaion is successful"
    assert (
        await authenticator.should_update(cli.session, base_url) is False
    ), "Update is not needed after authentication"
