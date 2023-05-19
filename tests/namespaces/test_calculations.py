"Test MetisCalculationsNamespace"

import asyncio
import json
from contextlib import nullcontext as does_not_raise
from copy import deepcopy
from datetime import datetime
from typing import List

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from aiohttp.web_exceptions import HTTPNotFound, HTTPOk
from yarl import URL

from metis_client import MetisAPI, MetisAPIAsync, MetisTokenAuth
from metis_client.dtos import MetisCalculationDTO, MetisErrorDTO, MetisRequestIdDTO
from metis_client.dtos.datasource import DataSourceType
from metis_client.exc import MetisPayloadException, MetisQuotaException
from metis_client.models import MetisMessageEvent
from tests.helpers import random_word
from tests.namespaces.test_datasources import (
    DS_ID,
    PATH_DS_POST_RESPONSE_PAYLOAD,
    make_datasources_event,
)

dt = datetime.fromordinal(1)
TOKEN = random_word(10)
CALC_ID = 10
PATH_STREAM = "/stream"
PATH_PING = "/v0"
PATH_C = "/v0/calculations"
PATH_C_ID = "/v0/calculations/{id}"
PATH_C_ENGINES = "/v0/calculations/engines"
PATH_C_POST_RESPONSE_PAYLOAD: MetisCalculationDTO = {
    "id": CALC_ID,
    "name": random_word(10),
    "userId": 1,
    "progress": 1,
    "result": [],
    "createdAt": dt,
    "updatedAt": dt,
    "parent": DS_ID,
}
PATH_C_POST_RESPONSE_ERROR_PAYLOAD: MetisErrorDTO = {"status": 400, "error": "oops"}
PATH_C_GET_RESPONSE_PAYLOAD = deepcopy(PATH_C_POST_RESPONSE_PAYLOAD)
PATH_C_GET_RESPONSE_ERROR_PAYLOAD: MetisErrorDTO = {"status": 402, "error": "oops"}
PATH_C_DELETE_RESPONSE_ERROR_PAYLOAD = deepcopy(PATH_C_POST_RESPONSE_ERROR_PAYLOAD)
PATH_C_DELETE_RESPONSE_ERROR404_PAYLOAD = {
    "status": HTTPNotFound.status_code,
    "error": "not found",
}
PATH_C_GET_ENGINES_RESPONSE = ["dummy", "other"]

event_stream: List[MetisMessageEvent] = []


def make_calculations_event(req_id: str, datas) -> MetisMessageEvent:
    "Create calculations event with content"
    evt_data_dto = {"reqId": req_id, "data": datas, "total": 1, "types": []}
    return MetisMessageEvent(
        "calculations", "calculations", json.dumps(evt_data_dto), "", ""
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
    evt = MetisMessageEvent("", "", "pong", "", "")
    event_stream.append(evt)
    return web.Response(status=HTTPOk.status_code)


async def calculation_create_handler(request: web.Request) -> web.Response:
    "Request handler"
    body: MetisRequestIdDTO = {"reqId": random_word(10)}

    payload = await request.json()
    if payload.get("engine") == "dummy":
        cal_dto = {
            **PATH_C_POST_RESPONSE_PAYLOAD,
            "createdAt": dt.isoformat(),
            "updatedAt": dt.isoformat(),
        }
        evt = make_calculations_event(body["reqId"], [cal_dto])
        event_stream.append(evt)
    elif payload.get("engine") == "results":
        cal_dto = {
            **PATH_C_POST_RESPONSE_PAYLOAD,
            "createdAt": dt.isoformat(),
            "updatedAt": dt.isoformat(),
            "progress": 25,
            "parent": payload["dataId"],
        }
        event_stream.append(make_calculations_event(body["reqId"], [cal_dto]))
        event_stream.append(
            make_calculations_event(body["reqId"], [{**cal_dto, "progress": 50}])
        )
        event_stream.append(make_calculations_event(body["reqId"], []))
        event_stream.append(
            make_calculations_event(body["reqId"], [{**cal_dto, "progress": 75}])
        )
        ds_dto = {
            **PATH_DS_POST_RESPONSE_PAYLOAD,
            "createdAt": dt.isoformat(),
            "updatedAt": dt.isoformat(),
            "parents": [payload["dataId"]],
            "type": DataSourceType.PROPERTY,
        }
        event_stream.append(
            make_calculations_event(body["reqId"], [{**ds_dto, "progress": 100}])
        )
        event_stream.append(make_datasources_event(body["reqId"], [ds_dto]))
    else:
        evt = make_error_event(body["reqId"], [PATH_C_POST_RESPONSE_ERROR_PAYLOAD])
        event_stream.append(evt)

    return web.json_response(body, status=HTTPOk.status_code)


async def list_calculations_handler(request: web.Request) -> web.Response:
    "Request handler"
    auth_header = request.headers.get("Authorization", "")
    body: MetisRequestIdDTO = {"reqId": random_word(10)}

    if auth_header != f"Bearer {str(True)}":
        ds_dto = {
            **PATH_C_GET_RESPONSE_PAYLOAD,
            "createdAt": dt.isoformat(),
            "updatedAt": dt.isoformat(),
        }
        evt = make_calculations_event(body["reqId"], [ds_dto])
    else:
        evt = make_error_event(body["reqId"], [PATH_C_GET_RESPONSE_ERROR_PAYLOAD])

    event_stream.append(evt)

    return web.json_response(body, status=HTTPOk.status_code)


async def cancel_calculations_handler(request: web.Request) -> web.Response:
    "Request handler"

    if request.match_info.get("id") not in ["1", "2"]:
        return web.Response(status=HTTPNotFound.status_code)

    body: MetisRequestIdDTO = {"reqId": random_word(10)}

    if request.match_info.get("id") == "2":
        evt = make_error_event(body["reqId"], [PATH_C_DELETE_RESPONSE_ERROR_PAYLOAD])
    else:
        evt = make_calculations_event(body["reqId"], [])

    event_stream.append(evt)

    return web.json_response(body, status=HTTPOk.status_code)


async def get_engines_handler(_: web.Request) -> web.Response:
    "Request handler"
    return web.json_response(PATH_C_GET_ENGINES_RESPONSE, status=HTTPOk.status_code)


async def create_app() -> web.Application:
    "Create web application"
    app = web.Application()
    app.router.add_head(PATH_PING, ping_handler)
    app.router.add_get(PATH_STREAM, sse_handler)
    app.router.add_post(PATH_C, calculation_create_handler)
    app.router.add_get(PATH_C, list_calculations_handler)
    app.router.add_get(PATH_C_ENGINES, get_engines_handler)
    app.router.add_delete(PATH_C_ID, cancel_calculations_handler)
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
    "engine, expected, raises",
    [
        ("dummy", PATH_C_POST_RESPONSE_PAYLOAD, does_not_raise()),
        ("fail", None, pytest.raises(MetisPayloadException)),
    ],
)
async def test_create_calculation(
    client: MetisAPI, client_async: MetisAPIAsync, engine, expected, raises
):
    "Test create()"
    with raises:
        cal = await client_async.v0.calculations.create(1, engine)
        assert cal == expected, "Response matches"
    with raises:
        cal = await asyncio.get_event_loop().run_in_executor(
            None, client.v0.calculations.create, 1, engine
        )
        assert cal == expected, "Response matches"


@pytest.mark.parametrize(
    "early_exit, sync, create",
    [
        (True, True, True),
        (False, True, False),
        (False, False, True),
        (False, False, False),
    ],
)
async def test_get_results(
    client: MetisAPI,
    client_async: MetisAPIAsync,
    early_exit: bool,
    sync: bool,
    create: bool,
):
    "Test get_results() and create_get_results()"

    def on_progress(calc: MetisCalculationDTO):
        assert on_progress.progress <= calc.get("progress", 0)
        on_progress.progress = calc.get("progress", 0)
        return not early_exit

    async def async_on_progress(calc: MetisCalculationDTO):
        return on_progress(calc)

    on_progress.progress = 0

    if sync:
        if create:
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                client.v0.calculations.create_get_results,
                DS_ID,
                "results",
                None,
                on_progress,
            )
        else:
            calc = await asyncio.get_event_loop().run_in_executor(
                None, client.v0.calculations.create, DS_ID, "results"
            )
            assert calc and calc["id"] == CALC_ID
            results = await asyncio.get_event_loop().run_in_executor(
                None, client.v0.calculations.get_results, calc["id"], on_progress
            )
    else:
        if create:
            results = await client_async.v0.calculations.create_get_results(
                DS_ID, "results", None, async_on_progress
            )
        else:
            calc = await client_async.v0.calculations.create(DS_ID, "results")
            assert calc and calc["id"] == CALC_ID
            results = await client_async.v0.calculations.get_results(
                calc["id"], async_on_progress
            )

    if early_exit:
        assert results is None
    else:
        assert results and DS_ID in results[0].get("parents", [])


@pytest.mark.parametrize(
    "fail, expected, raises",
    [
        (False, [PATH_C_GET_RESPONSE_PAYLOAD], does_not_raise()),
        (True, None, pytest.raises(MetisQuotaException)),
    ],
)
async def test_list_calculations(base_url: URL, fail: bool, expected, raises):
    "Test list()"
    with raises:
        async with MetisAPIAsync(base_url, auth=MetisTokenAuth(str(fail))) as client:
            cal = await client.v0.calculations.list()
        assert cal == expected, "Response matches"
    with raises:
        client = MetisAPI(base_url, auth=MetisTokenAuth(str(fail)))
        cal = await asyncio.get_event_loop().run_in_executor(
            None, client.v0.calculations.list
        )
        assert cal == expected, "Response matches"


@pytest.mark.parametrize(
    "calc_id, fail, expected, raises",
    [
        (CALC_ID, False, PATH_C_GET_RESPONSE_PAYLOAD, does_not_raise()),
        (-1, False, None, does_not_raise()),
        (-1, True, None, pytest.raises(MetisQuotaException)),
    ],
)
async def test_get_calculation(
    base_url: URL, calc_id: int, fail: bool, expected, raises
):
    "Test get()"
    with raises:
        async with MetisAPIAsync(base_url, auth=MetisTokenAuth(str(fail))) as client:
            cal = await client.v0.calculations.get(calc_id)
        assert cal == expected, "Response matches"
    with raises:
        client = MetisAPI(base_url, auth=MetisTokenAuth(str(fail)))
        cal = await asyncio.get_event_loop().run_in_executor(
            None, client.v0.calculations.get, calc_id
        )
        assert cal == expected, "Response matches"


@pytest.mark.parametrize(
    "cal_id, raises",
    [
        (1, does_not_raise()),
        (2, pytest.raises(MetisPayloadException)),
    ],
)
async def test_cancel_calculation(
    client: MetisAPI, client_async: MetisAPIAsync, cal_id: int, raises
):
    "Test delete()"
    with raises:
        await client_async.v0.calculations.cancel(cal_id)
    with raises:
        await asyncio.get_event_loop().run_in_executor(
            None, client.v0.calculations.cancel, cal_id
        )


async def test_get_engines(client: MetisAPI, client_async: MetisAPIAsync):
    "Test get_engines()"
    en_async = await client_async.v0.calculations.get_engines()
    en_sync = await asyncio.get_event_loop().run_in_executor(
        None, client.v0.calculations.get_engines
    )
    assert en_async == en_sync, "Response matches"
    assert en_sync == PATH_C_GET_ENGINES_RESPONSE, "Response matches"
