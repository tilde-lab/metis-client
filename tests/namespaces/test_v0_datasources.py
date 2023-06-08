"Test MetisV0DatasourcesNamespace"

import asyncio
import json
from contextlib import nullcontext as does_not_raise
from copy import deepcopy
from datetime import datetime
from functools import partial
from typing import List

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from aiohttp.web_exceptions import HTTPNotFound, HTTPOk
from freezegun import freeze_time
from yarl import URL

from metis_client import MetisAPI, MetisAPIAsync, MetisTokenAuth
from metis_client.dtos import (
    MetisDataSourceContentOnlyDTO,
    MetisDataSourceDTO,
    MetisErrorDTO,
    MetisRequestIdDTO,
)
from metis_client.exc import (
    MetisNotFoundException,
    MetisPayloadException,
    MetisQuotaException,
)
from metis_client.models import MetisMessageEvent
from tests.helpers import random_word

dt = datetime.fromordinal(1)
DS_ID = 1
PARENT_DS_ID = 2
CHILD_DS_ID = 3
TOKEN = random_word(10)
PATH_STREAM = "/stream"
PATH_PING = "/v0"
PATH_DS = "/v0/datasources"
PATH_DS_ID = "/v0/datasources/{id}"
PATH_DS_POST_RESPONSE_PAYLOAD: MetisDataSourceDTO = {
    "id": DS_ID,
    "userId": 1,
    "userFirstName": random_word(10),
    "userLastName": random_word(10),
    "userEmail": random_word(10),
    "name": random_word(10),
    "content": random_word(10),
    "type": 1,
    "collections": [],
    "createdAt": dt,
    "updatedAt": dt,
    "parents": [PARENT_DS_ID],
    "children": [CHILD_DS_ID],
}
PATH_DS_POST_RESPONSE_ERROR_PAYLOAD: MetisErrorDTO = {"status": 400, "error": "oops"}
PATH_DS_GET_RESPONSE_PAYLOAD = deepcopy(PATH_DS_POST_RESPONSE_PAYLOAD)
PATH_DS_GET_RESPONSE_ERROR_PAYLOAD: MetisErrorDTO = {
    "status": 402,
    "error": {"message": "oops"},
}
PATH_DS_DELETE_RESPONSE_ERROR_PAYLOAD = deepcopy(PATH_DS_POST_RESPONSE_ERROR_PAYLOAD)
PATH_DS_DELETE_RESPONSE_ERROR404_PAYLOAD = {
    "status": HTTPNotFound.status_code,
    "error": "not found",
}
PATH_DS_ID_GET_RESPONSE: MetisDataSourceContentOnlyDTO = {"content": random_word(10)}

event_stream: List[MetisMessageEvent] = []


def make_datasources_event(req_id: str, datas) -> MetisMessageEvent:
    "Create datasources event with content"
    evt_data_dto = {"reqId": req_id, "data": datas, "total": 1, "types": []}
    return MetisMessageEvent(
        "datasources", "datasources", json.dumps(evt_data_dto), "", ""
    )


def make_error_event(req_id: str, datas) -> MetisMessageEvent:
    "Create errors event with content"
    evt_data_dto = {"reqId": req_id, "data": datas}
    return MetisMessageEvent("errors", "errors", json.dumps(evt_data_dto), "", "")


async def sse_handler(_: web.Request) -> web.Response:
    "Request handler"
    body = "".join(
        [f"event: {evt.type}\ndata: {evt.data}\n\n\n" for evt in event_stream]
    )
    resp = web.Response(status=HTTPOk.status_code, body=body)
    resp.content_type = "text/event-stream"
    resp.headers["Cache-Control"] = "no-store"
    return resp


async def ping_handler(_) -> web.Response:
    "Request handler"
    evt = MetisMessageEvent("", "ping", "", "", "")
    event_stream.append(evt)
    return web.Response(status=HTTPOk.status_code)


async def datasource_create_handler(request: web.Request) -> web.Response:
    "Request handler"
    body: MetisRequestIdDTO = {"reqId": random_word(10)}

    payload = await request.json()
    if payload.get("content") == "ok":
        ds_dto = {
            **PATH_DS_POST_RESPONSE_PAYLOAD,
            "createdAt": dt.isoformat(),
            "updatedAt": dt.isoformat(),
        }
        evt = make_datasources_event(body["reqId"], [ds_dto])
    else:
        evt = make_error_event(body["reqId"], [PATH_DS_POST_RESPONSE_ERROR_PAYLOAD])

    event_stream.append(evt)

    return web.json_response(body, status=HTTPOk.status_code)


async def list_datasources_handler(request: web.Request) -> web.Response:
    "Request handler"
    auth_header = request.headers.get("Authorization", "")
    body: MetisRequestIdDTO = {"reqId": random_word(10)}

    if auth_header == "Bearer slow":
        await asyncio.sleep(10)

    if auth_header != f"Bearer {str(True)}":
        ds_dto = {
            **PATH_DS_GET_RESPONSE_PAYLOAD,
            "createdAt": dt.isoformat(),
            "updatedAt": dt.isoformat(),
        }
        evt = make_datasources_event(body["reqId"], [ds_dto])
    else:
        evt = make_error_event(body["reqId"], [PATH_DS_GET_RESPONSE_ERROR_PAYLOAD])

    event_stream.append(evt)

    return web.json_response(body, status=HTTPOk.status_code)


async def delete_datasource_handler(request: web.Request) -> web.Response:
    "Request handler"

    if request.match_info.get("id") not in ["1", "2"]:
        return web.Response(status=HTTPNotFound.status_code)

    body: MetisRequestIdDTO = {"reqId": random_word(10)}

    if request.match_info.get("id") == "2":
        evt = make_error_event(body["reqId"], [PATH_DS_DELETE_RESPONSE_ERROR_PAYLOAD])
    else:
        evt = make_datasources_event(body["reqId"], [])

    event_stream.append(evt)

    return web.json_response(body, status=HTTPOk.status_code)


async def get_datasource_handler(request: web.Request) -> web.Response:
    "Request handler"
    if request.match_info.get("id") == "2":
        # stupid variant of success with error
        return web.json_response(
            PATH_DS_DELETE_RESPONSE_ERROR404_PAYLOAD, status=HTTPOk.status_code
        )
    if request.match_info.get("id") not in ["1", "2"]:
        return web.json_response(
            PATH_DS_DELETE_RESPONSE_ERROR404_PAYLOAD, status=HTTPNotFound.status_code
        )
    return web.json_response(PATH_DS_ID_GET_RESPONSE, status=HTTPOk.status_code)


async def create_app() -> web.Application:
    "Create web application"
    app = web.Application()
    app.router.add_head(PATH_PING, ping_handler)
    app.router.add_get(PATH_STREAM, sse_handler)
    app.router.add_post(PATH_DS, datasource_create_handler)
    app.router.add_get(PATH_DS, list_datasources_handler)
    app.router.add_get(PATH_DS_ID, get_datasource_handler)
    app.router.add_delete(PATH_DS_ID, delete_datasource_handler)
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


@pytest.mark.parametrize(
    "content, expected, raises",
    [
        ("ok", PATH_DS_POST_RESPONSE_PAYLOAD, does_not_raise()),
        ("fail", None, pytest.raises(MetisPayloadException)),
    ],
)
async def test_create_datasource(
    client: MetisAPI, client_async: MetisAPIAsync, content, expected, raises
):
    "Test create()"
    with raises:
        src = await client_async.v0.datasources.create(content)
        assert src == expected, "Response matches"
    with raises:
        src = await asyncio.get_event_loop().run_in_executor(
            None, client.v0.datasources.create, content
        )
        assert src == expected, "Response matches"


@pytest.mark.parametrize(
    "fail, expected, raises",
    [
        (False, [PATH_DS_GET_RESPONSE_PAYLOAD], does_not_raise()),
        (True, None, pytest.raises(MetisQuotaException)),
    ],
)
async def test_list_datasources(base_url: URL, fail: bool, expected, raises):
    "Test list()"
    with raises:
        async with MetisAPIAsync(base_url, auth=MetisTokenAuth(str(fail))) as client:
            src = await client.v0.datasources.list()
        assert src == expected, "Response matches"
    with raises:
        client = MetisAPI(base_url, auth=MetisTokenAuth(str(fail)))
        src = await asyncio.get_event_loop().run_in_executor(
            None, client.v0.datasources.list
        )
        assert src == expected, "Response matches"


@freeze_time("1970-01-01", auto_tick_seconds=10)
async def test_timeout(base_url: URL, client: MetisAPI):
    "Test timeout"
    client = MetisAPI(base_url, auth=MetisTokenAuth("slow"))
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.get_event_loop().run_in_executor(
            None, partial(client.v0.datasources.list, timeout=1)
        )


@pytest.mark.parametrize(
    "method_name, data_id, fail, expected, raises",
    [
        # get()
        ("get", -1, True, None, pytest.raises(MetisQuotaException)),
        ("get", DS_ID, False, PATH_DS_GET_RESPONSE_PAYLOAD, does_not_raise()),
        ("get", PARENT_DS_ID, False, None, does_not_raise()),
        # get_parents()
        (
            "get_parents",
            CHILD_DS_ID,
            False,
            [PATH_DS_GET_RESPONSE_PAYLOAD],
            does_not_raise(),
        ),
        ("get_parents", DS_ID, False, [], does_not_raise()),
        # get_children()
        (
            "get_children",
            PARENT_DS_ID,
            False,
            [PATH_DS_GET_RESPONSE_PAYLOAD],
            does_not_raise(),
        ),
        ("get_children", DS_ID, False, [], does_not_raise()),
    ],
)
async def test_get_datasource(
    base_url: URL, method_name: str, data_id: int, fail: bool, expected, raises
):
    "Test get(), get_parents(), get_children()"
    with raises:
        async with MetisAPIAsync(base_url, auth=MetisTokenAuth(str(fail))) as client:
            method = getattr(client.v0.datasources, method_name)
            src = await method(data_id)
        assert src == expected, "Response matches"
    with raises:
        client = MetisAPI(base_url, auth=MetisTokenAuth(str(fail)))
        method = getattr(client.v0.datasources, method_name)
        src = await asyncio.get_event_loop().run_in_executor(None, method, data_id)
        assert src == expected, "Response matches"


@pytest.mark.parametrize(
    "ds_id, raises",
    [
        (1, does_not_raise()),
        (2, pytest.raises(MetisPayloadException)),
        (3, pytest.raises(MetisNotFoundException)),
    ],
)
async def test_delete_datasource(
    client: MetisAPI, client_async: MetisAPIAsync, ds_id: int, raises
):
    "Test delete()"
    with raises:
        await client_async.v0.datasources.delete(ds_id)
    with raises:
        await asyncio.get_event_loop().run_in_executor(
            None, client.v0.datasources.delete, ds_id
        )


@pytest.mark.parametrize(
    "ds_id, raises",
    [
        (1, does_not_raise()),
        (2, pytest.raises(MetisNotFoundException)),
        (3, pytest.raises(MetisNotFoundException)),
    ],
)
async def test_get_datasource_contents(
    client: MetisAPI, client_async: MetisAPIAsync, ds_id, raises
):
    "Test get_content()"
    with raises:
        res = await client_async.v0.datasources.get_content(ds_id)
        assert res == PATH_DS_ID_GET_RESPONSE, "Response matches"
    with raises:
        res = await asyncio.get_event_loop().run_in_executor(
            None, client.v0.datasources.get_content, ds_id
        )
        assert res == PATH_DS_ID_GET_RESPONSE, "Response matches"
