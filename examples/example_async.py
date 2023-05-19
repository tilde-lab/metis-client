#!/usr/bin/env python3
"""Example of usage of asynchronous client"""

import asyncio
import sys

from metis_client import MetisAPIAsync, MetisTokenAuth
from metis_client.dtos.calculation import MetisCalculationDTO

API_URL = "http://localhost:3000"
TEST_ENGINE = "dummy"

try:
    with open(sys.argv[1], encoding="utf-8") as fp:
        CONTENT = fp.read()
except IndexError:
    # pylint: disable=line-too-long
    CONTENT = """{"attributes":{"immutable_id":42, "species":[{"chemical_symbols":
["Au"]}],"cartesian_site_positions":[[0,0,0]],"lattice_vectors":[[0,2,2],[2,0,2],[2,2,0]]}}"""


async def on_progress_log(calc: MetisCalculationDTO):
    "Print progress"
    print("Progress:", calc.get("progress"))


async def create_calc_then_get_results(client: MetisAPIAsync):
    "Create data source, run calculation, then wait for the results"

    data = await client.v0.datasources.create(CONTENT)
    assert data

    calc = await client.v0.calculations.create(data.get("id"), engine=TEST_ENGINE)
    assert calc

    results = await client.v0.calculations.get_results(
        calc["id"], on_progress=on_progress_log
    )
    print(results)
    assert results
    print("=" * 50 + "Test passed")


async def create_calc_and_get_results(client: MetisAPIAsync):
    "Create data source, run calculation and wait for the results"

    data = await client.v0.datasources.create(CONTENT)
    assert data

    results = await client.v0.calculations.create_get_results(
        data["id"], engine=TEST_ENGINE, on_progress=on_progress_log
    )
    print(results)
    assert results
    print("=" * 50 + "Test passed")


async def create_calc_then_cancel(client: MetisAPIAsync):
    """
    Create data source. Run calculation.
    Stop watching calculation on 50%, cancel calculation.
    """

    data = await client.v0.datasources.create(CONTENT)
    assert data

    async def stop_watching_on_half(calc: MetisCalculationDTO):
        await on_progress_log(calc)
        return calc.get("progress") < 50

    calc = await client.v0.calculations.create(data.get("id"), engine=TEST_ENGINE)
    assert calc

    results = await client.v0.calculations.get_results(
        calc["id"], on_progress=stop_watching_on_half
    )
    assert results is None
    await client.v0.calculations.cancel(calc["id"])
    print("=" * 50 + "Test passed")


async def main():
    "Run all examples"
    async with MetisAPIAsync(API_URL, auth=MetisTokenAuth("admin@test.com")) as client:
        print(await client.v0.auth.whoami())
        print(
            "The following engines are available:",
            await client.v0.calculations.get_engines(),
        )

        await create_calc_then_get_results(client)
        await create_calc_and_get_results(client)
        await create_calc_then_cancel(client)


asyncio.run(main())
