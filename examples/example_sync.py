#!/usr/bin/env python3
"""Example of usage of synchronous client"""
# pylint: disable=no-value-for-parameter

import sys

from metis_client import MetisAPI, MetisTokenAuth

API_URL = "http://localhost:3000"

try:
    with open(sys.argv[1], encoding="utf-8") as fp:
        CONTENT = fp.read()
except IndexError:
    CONTENT = """{"attributes":{"immutable_id":42, "species":[{"chemical_symbols":
["Au"]}],"cartesian_site_positions":[[0,0,0]],"lattice_vectors":[[0,2,2],[2,0,2],[2,2,0]]}}"""


client = MetisAPI(API_URL, auth=MetisTokenAuth("admin@test.com"))

print(client.v0.auth.whoami())
data = client.v0.datasources.create(CONTENT)
if not data:
    print(data)
    sys.exit(1)

calc = client.v0.calculations.create(data["id"])
print(calc)
if not calc:
    sys.exit(1)
print("=" * 100 + "Test passed")
