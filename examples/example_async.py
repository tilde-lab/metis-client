#!/usr/bin/env python3

import signal
import sys

from anyio import CancelScope, create_task_group, open_signal_receiver, run
from yarl import URL

from metis_client import MetisAPIAsync, MetisTokenAuth
from metis_client.models import MetisCalculationModel, MetisDataSourceModel

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
        data = await client.v0.datasources.create(content)
        if not isinstance(data, MetisDataSourceModel):
            return

        calc = await client.v0.calculations.create(data.id)
        if not isinstance(calc, MetisCalculationModel):
            return
        print(calc)
        print("=" * 100 + "Test passed")


async def main():
    async with create_task_group() as tg:
        tg.start_soon(signal_handler, tg.cancel_scope)
        await job()
        tg.cancel_scope.cancel()


run(main)
