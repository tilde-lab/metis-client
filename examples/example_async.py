#!/usr/bin/env python3
"""Example of usage of asynchronous client"""

import asyncio
import sys

from metis_client import MetisAPIAsync, MetisTokenAuth

API_URL = "http://localhost:3000"

try:
    with open(sys.argv[1], encoding="utf-8") as fp:
        CONTENT = fp.read()
except IndexError:
    # pylint: disable=line-too-long
    CONTENT = """{"attributes":{"immutable_id":42, "species":[{"chemical_symbols":
["Au"]}],"cartesian_site_positions":[[0,0,0]],"lattice_vectors":[[0,2,2],[2,0,2],[2,2,0]]}}"""


async def main():
    "Do work"
    async with MetisAPIAsync(API_URL, auth=MetisTokenAuth("admin@test.com")) as client:
        print(await client.v0.auth.whoami())
        data = await client.v0.datasources.create(CONTENT)
        if not data:
            return

        calc = await client.v0.calculations.create(data.get("id"))
        if not calc:
            return
        print(calc)
        print("=" * 100 + "Test passed")


asyncio.run(main())
