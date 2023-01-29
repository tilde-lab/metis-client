#!/usr/bin/env python3

import sys
import signal

import aiohttp
from anyio import CancelScope, run, open_signal_receiver, create_task_group
from yarl import URL

from metis_client import MetisAPI, MetisLocalUserAuth, MetisTokenAuth
from metis_client.models.event import MetisDataSourcesEventModel, MetisCalculationsEventModel


API_URL = URL("http://localhost:3000")

try: content = open(sys.argv[1]).read()
except IndexError: content = """{"attributes":{"immutable_id":42, "species":[{"chemical_symbols":
["Au"]}],"cartesian_site_positions":[[0,0,0]],"lattice_vectors":[[0,2,2],[2,0,2],[2,2,0]]}}"""

async def on_request_start(session, trace_config_ctx, params):
    print("Starting request")
    #print(params)

async def on_request_end(session, trace_config_ctx, params):
    print("Ending request")
    #print(params)
    #print(await params.response.text())

async def signal_handler(scope: CancelScope):
    with open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
        async for signum in signals:
            if signum == signal.SIGINT:
                print("Ctrl+C pressed!")
            else:
                print("Terminated!")

            scope.cancel()
            return

trace_config = aiohttp.TraceConfig()
trace_config.on_request_start.append(on_request_start)
trace_config.on_request_end.append(on_request_end)

async def job():
    async with MetisAPI(
        API_URL,
        MetisTokenAuth("admin@test.com"),
        trace_configs=[trace_config],
    ) as client:
        async with client.stream.subscribe() as sub:
            await client.v0.ping()
            print(await client.v0.auth.whoami())
            req = await client.v0.datasources.create(content)
            answer = None
            async for msg in sub:
                if (
                    isinstance(msg, MetisDataSourcesEventModel)
                    and msg.request_id == req.request_id
                ):
                    answer = msg
                    break
            if not answer or not answer.data:
                return None
            data_id = sorted(answer.data, key=lambda x: x.created_at)[-1].id
            req = await client.v0.calculations.create(data_id)
            async for msg in sub:
                if (
                    isinstance(msg, MetisCalculationsEventModel)
                    and msg.request_id == req.request_id
                ):
                    answer = msg
                    break
            print(answer)
            print('=' * 100 + 'Test passed')

async def main():
    async with create_task_group() as tg:
        tg.start_soon(signal_handler, tg.cancel_scope)
        await job()
        tg.cancel_scope.cancel()

run(main)
