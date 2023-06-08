#!/usr/bin/env python3
"""Example of usage of synchronous client"""
# pylint: disable=no-value-for-parameter

import asyncio
import sys

from metis_client import MetisAPI, MetisTokenAuth
from metis_client.dtos import MetisCalculationDTO

API_URL = "http://localhost:3000"
TEST_ENGINE = "dummy"

try:
    with open(sys.argv[1], encoding="utf-8") as fp:
        CONTENT = fp.read()
except IndexError:
    # pylint: disable=line-too-long
    CONTENT = """{"attributes":{"immutable_id":42, "species":[{"chemical_symbols":
["Au"]}],"cartesian_site_positions":[[0,0,0]],"lattice_vectors":[[0,2,2],[2,0,2],[2,2,0]]}}"""


def on_progress_log(calc: MetisCalculationDTO):
    "Print progress"
    print("Progress:", calc.get("progress"))


def create_calc_then_get_results(client: MetisAPI):
    "Create data source, run calculation, then wait for the results"

    data = client.v0.datasources.create(CONTENT)
    assert data

    calc = client.v0.calculations.create(data.get("id"), engine=TEST_ENGINE)
    assert calc

    results = client.v0.calculations.get_results(
        calc["id"], on_progress=on_progress_log
    )
    print(results)
    assert results
    print("=" * 50 + "Test passed")


def create_calc_and_get_results(client: MetisAPI):
    "Create data source, run calculation and wait for the results"

    data = client.v0.datasources.create(CONTENT)
    assert data

    results = client.v0.calculations.create_get_results(
        data["id"], engine=TEST_ENGINE, on_progress=on_progress_log
    )
    print(results)
    assert results
    print("=" * 50 + "Test passed")


def create_calc_then_cancel(client: MetisAPI):
    """
    Create data source. Run calculation.
    Stop watching calculation on 50%, cancel calculation.
    """

    data = client.v0.datasources.create(CONTENT)
    assert data

    def stop_watching_on_half(calc: MetisCalculationDTO):
        on_progress_log(calc)
        return calc.get("progress") < 50

    calc = client.v0.calculations.create(data.get("id"), engine=TEST_ENGINE)
    assert calc

    results = client.v0.calculations.get_results(
        calc["id"], on_progress=stop_watching_on_half
    )
    assert results is None
    client.v0.calculations.cancel(calc["id"])
    print("=" * 50 + "Test passed")


def create_calc_timeout_cancel(client: MetisAPI):
    """
    Create data source. Run calculation.
    Cancel calculation on timeout.
    """

    data = client.v0.datasources.create(CONTENT)
    assert data

    calc = client.v0.calculations.create(data.get("id"), engine=TEST_ENGINE)
    assert calc

    try:
        results = client.v0.calculations.get_results(calc["id"], timeout=1)
        assert results is None
    except asyncio.TimeoutError:
        print("Timeouted as planned")
        client.v0.calculations.cancel(calc["id"])
    print("=" * 50 + "Test passed")


def main():
    "Run all examples"

    client = MetisAPI(API_URL, auth=MetisTokenAuth("admin@test.com"), timeout=60)

    print(client.v0.auth.whoami())
    print("The following engines are available:", client.calculations.supported())

    create_calc_then_get_results(client)
    create_calc_and_get_results(client)
    create_calc_then_cancel(client)
    create_calc_timeout_cancel(client)


main()
