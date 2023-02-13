#!/usr/bin/env python3

import sys

from yarl import URL

from metis_client import MetisAPI, MetisTokenAuth
from metis_client.models import MetisCalculationModel, MetisDataSourceModel

API_URL = URL("http://localhost:3000")

try:
    content = open(sys.argv[1]).read()
except IndexError:
    content = """{"attributes":{"immutable_id":42, "species":[{"chemical_symbols":
["Au"]}],"cartesian_site_positions":[[0,0,0]],"lattice_vectors":[[0,2,2],[2,0,2],[2,2,0]]}}"""


client = MetisAPI(API_URL, auth=MetisTokenAuth("admin@test.com"))

print(client.v0.auth.whoami())
data = client.v0.datasources.create(content)
if not isinstance(data, MetisDataSourceModel):
    print(data)
    exit(1)

calc = client.v0.calculations.create(data.id)
print(calc)
if isinstance(calc, MetisCalculationModel):
    print("=" * 100 + "Test passed")
