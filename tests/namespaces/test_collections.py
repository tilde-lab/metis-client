"Test MetisCollectionsNamespace"

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
from yarl import URL

from metis_client import MetisAPI, MetisAPIAsync, MetisTokenAuth
from metis_client.dtos import (
    MetisCollectionCreateDTO,
    MetisCollectionDTO,
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
TOKEN = random_word(10)
PATH_STREAM = "/stream"
PATH_PING = "/v0"
PATH_C = "/v0/collections"
PATH_C_ID = "/v0/collections/{id}"
PATH_C_PUT_PAYLOAD: MetisCollectionCreateDTO = {
    "title": random_word(10),
    "typeId": 1,
    "dataSources": [1, 2, 3],
    "users": [1, 2, 3],
    "description": random_word(10),
}
PATH_C_PUT_RESPONSE_PAYLOAD: MetisCollectionDTO = {
    **PATH_C_PUT_PAYLOAD,
    "createdAt": dt,
    "updatedAt": dt,
}
PATH_C_PUT_RESPONSE_ERROR_PAYLOAD: MetisErrorDTO = {"status": 400, "error": "oops"}
PATH_C_GET_RESPONSE_PAYLOAD = deepcopy(PATH_C_PUT_RESPONSE_PAYLOAD)
PATH_C_GET_RESPONSE_ERROR_PAYLOAD: MetisErrorDTO = {"status": 402, "error": "oops"}
PATH_C_DELETE_RESPONSE_ERROR_PAYLOAD = deepcopy(PATH_C_PUT_RESPONSE_ERROR_PAYLOAD)
PATH_C_DELETE_RESPONSE_ERROR404_PAYLOAD = {
    "status": HTTPNotFound.status_code,
    "error": "not found",
}

event_stream: List[MetisMessageEvent] = []


def make_collections_event(req_id: str, datas) -> MetisMessageEvent:
    "Create collections event with content"
    evt_data_dto = {"reqId": req_id, "data": datas, "total": 1, "types": []}
    return MetisMessageEvent(
        "collections", "collections", json.dumps(evt_data_dto), "", ""
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


async def collection_create_handler(request: web.Request) -> web.Response:
    "Request handler"
    body: MetisRequestIdDTO = {"reqId": random_word(10)}

    payload = await request.json()
    if payload.get("typeId") == 1:
        collection_dto = {
            **payload,
            "createdAt": dt.isoformat(),
            "updatedAt": dt.isoformat(),
        }
        evt = make_collections_event(body["reqId"], [collection_dto])
    else:
        evt = make_error_event(body["reqId"], [PATH_C_PUT_RESPONSE_ERROR_PAYLOAD])

    event_stream.append(evt)

    return web.json_response(body, status=HTTPOk.status_code)


async def list_collections_handler(request: web.Request) -> web.Response:
    "Request handler"
    auth_header = request.headers.get("Authorization", "")
    body: MetisRequestIdDTO = {"reqId": random_word(10)}

    if auth_header != f"Bearer {str(True)}":
        collection_dto = {
            **PATH_C_GET_RESPONSE_PAYLOAD,
            "createdAt": dt.isoformat(),
            "updatedAt": dt.isoformat(),
        }
        evt = make_collections_event(body["reqId"], [collection_dto])
    else:
        evt = make_error_event(body["reqId"], [PATH_C_GET_RESPONSE_ERROR_PAYLOAD])

    event_stream.append(evt)

    return web.json_response(body, status=HTTPOk.status_code)


async def delete_collection_handler(request: web.Request) -> web.Response:
    "Request handler"

    if request.match_info.get("id") not in ["1", "2"]:
        return web.Response(status=HTTPNotFound.status_code)

    body: MetisRequestIdDTO = {"reqId": random_word(10)}

    if request.match_info.get("id") == "2":
        evt = make_error_event(body["reqId"], [PATH_C_DELETE_RESPONSE_ERROR_PAYLOAD])
    else:
        evt = make_collections_event(body["reqId"], [])

    event_stream.append(evt)

    return web.json_response(body, status=HTTPOk.status_code)


async def create_app() -> web.Application:
    "Create web application"
    app = web.Application()
    app.router.add_head(PATH_PING, ping_handler)
    app.router.add_get(PATH_STREAM, sse_handler)
    app.router.add_put(PATH_C, collection_create_handler)
    app.router.add_get(PATH_C, list_collections_handler)
    app.router.add_delete(PATH_C_ID, delete_collection_handler)
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
    "type_id, expected, raises",
    [
        (1, PATH_C_PUT_RESPONSE_PAYLOAD, does_not_raise()),
        (2, None, pytest.raises(MetisPayloadException)),
    ],
)
async def test_create_collection(
    client: MetisAPI, client_async: MetisAPIAsync, type_id, expected, raises
):
    "Test create()"
    kwargs = {
        "type_id": type_id,
        "title": PATH_C_PUT_PAYLOAD["title"],
        "description": PATH_C_PUT_PAYLOAD["description"],
        "data_source_ids": PATH_C_PUT_PAYLOAD["dataSources"],
        "user_ids": PATH_C_PUT_PAYLOAD["users"],
    }
    with raises:
        col = await client_async.v0.collections.create(**kwargs)
        assert col == expected, "Response matches"
    with raises:
        col = await asyncio.get_event_loop().run_in_executor(
            None, partial(client.v0.collections.create, **kwargs)
        )
        assert col == expected, "Response matches"


@pytest.mark.parametrize(
    "fail, expected, raises",
    [
        (False, [PATH_C_GET_RESPONSE_PAYLOAD], does_not_raise()),
        (True, None, pytest.raises(MetisQuotaException)),
    ],
)
async def test_list_collections(base_url: URL, fail: bool, expected, raises):
    "Test list()"
    with raises:
        async with MetisAPIAsync(base_url, auth=MetisTokenAuth(str(fail))) as client:
            cols = await client.v0.collections.list()
        assert cols == expected, "Response matches"
    with raises:
        client = MetisAPI(base_url, auth=MetisTokenAuth(str(fail)))
        cols = await asyncio.get_event_loop().run_in_executor(
            None, client.v0.collections.list
        )
        assert cols == expected, "Response matches"


@pytest.mark.parametrize(
    "col_id, raises",
    [
        (1, does_not_raise()),
        (2, pytest.raises(MetisPayloadException)),
        (3, pytest.raises(MetisNotFoundException)),
    ],
)
async def test_delete_collection(
    client: MetisAPI, client_async: MetisAPIAsync, col_id: int, raises
):
    "Test delete()"
    with raises:
        await client_async.v0.collections.delete(col_id)
    with raises:
        await asyncio.get_event_loop().run_in_executor(
            None, client.v0.collections.delete, col_id
        )
