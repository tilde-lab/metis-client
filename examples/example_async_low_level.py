#!/usr/bin/env python3
"""Example of usage of asynchronous client with low-level methods"""

import asyncio
import sys
from datetime import datetime

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
        async with client.stream.subscribe() as sub:
            req = await client.v0.datasources.create_event(CONTENT)
            answer = None
            async for msg in sub:
                if msg["type"] == "datasources" and msg.get("data", {}).get(
                    "reqId"
                ) == req.get("reqId"):
                    answer = msg.get("data")
                    break
            if not answer:
                return None

            data_id = sorted(
                answer["data"],
                key=lambda x: x.get("createdAt", datetime.fromordinal(1)),
            )[-1].get("id")

            req = await client.v0.calculations.create_event(data_id)
            answer = None
            async for msg in sub:
                if msg["type"] == "calculations" and msg.get("data", {}).get(
                    "reqId"
                ) == req.get("reqId"):
                    data = msg.get("data", {}).get("data", [])
                    if data:
                        answer = data[-1]
                    break
            print(answer)
            print("=" * 100 + "Test passed")


asyncio.run(main())
