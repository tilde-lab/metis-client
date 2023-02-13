#!/usr/bin/env python3

import signal
import sys

from anyio import CancelScope, create_task_group, open_signal_receiver, run
from yarl import URL

from metis_client import MetisAPIAsync, MetisTokenAuth
from metis_client.models import MetisCalculationsEventModel, MetisDataSourcesEventModel

API_URL = URL("http://localhost:3000")

try:
    content = open(sys.argv[1]).read()
except IndexError:
    content = """{"attributes":{"immutable_id":42, "species":[{"chemical_symbols":
["Au"]}],"cartesian_site_positions":[[0,0,0]],"lattice_vectors":[[0,2,2],[2,0,2],[2,2,0]]}}"""


async def signal_handler(scope: CancelScope):
    with open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
        async for signum in signals:
            if signum == signal.SIGINT:
                print("Ctrl+C pressed!")
            else:
                print("Terminated!")

            scope.cancel()
            return


async def job():
    async with MetisAPIAsync(API_URL, auth=MetisTokenAuth("admin@test.com")) as client:
        print(await client.v0.auth.whoami())
        async with client.stream.subscribe() as sub:
            req = await client.v0.datasources.create_event(content)
            answer = None
            async for msg in sub:
                if (
                    MetisDataSourcesEventModel.guard(msg)
                    and msg.request_id == req.request_id
                ):
                    answer = msg
                    break
            if not answer or not answer.data:
                return None

            data_id = sorted(answer.data, key=lambda x: x.created_at)[-1].id
            req = await client.v0.calculations.create_event(data_id)
            async for msg in sub:
                if (
                    MetisCalculationsEventModel.guard(msg)
                    and msg.request_id == req.request_id
                ):
                    answer = msg
                    break
            print(answer)
            print("=" * 100 + "Test passed")


async def main():
    async with create_task_group() as tg:
        tg.start_soon(signal_handler, tg.cancel_scope)
        await job()
        tg.cancel_scope.cancel()


run(main)
