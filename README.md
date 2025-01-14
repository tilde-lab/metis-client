# Metis API client

[![DOI](https://zenodo.org/badge/563802198.svg)](https://doi.org/10.5281/zenodo.7693569)
[![PyPI](https://img.shields.io/pypi/v/metis_client.svg?style=flat)](https://pypi.org/project/metis-client)

<p align="center"><img src="https://github.com/metis-science/metis-client/blob/master/metis-client.png" width="300" /></p>

This library allows for programmatic interactions with the [Metis infrastructure](https://github.com/search?q=org%3Abasf+metis).


## Installation

`pip install metis_client`

## Usage

There are two client flavors: **asyncronous** `asyncio` client
and simplified **synchronous** client.

### Asynchronous client

An asynchronous client is `MetisAPIAsync`. Example of usage:

```python
from metis_client import MetisAPIAsync, MetisTokenAuth

async def main():
    async with MetisAPIAsync(API_URL, auth=MetisTokenAuth("VERY_SECRET_TOKEN")) as client:
        print(await client.v0.auth.whoami())
        data = await client.v0.datasources.create(content, name)
        results = await client.v0.calculations.create_get_results(data["id"])
        print(resuls)
```

See `examples` directory for more examples.

### Synchronous client

A synchronous client is `MetisAPI`. Example of usage:

```python
from metis_client import MetisAPI, MetisTokenAuth

client = MetisAPI(API_URL, auth=MetisTokenAuth("VERY_SECRET_TOKEN"), timeout=5)
data = client.v0.datasources.create(content, name)
results = client.v0.calculations.create_get_results(data["id"], timeout=False)
print(results)
```

NB in development one can replace a `VERY_SECRET_TOKEN` string with the development user email, e.g.
`admin@test.com` (refer to **users_emails** BFF table).


## Contributing

Please give a minute to the [contribution guide](https://github.com/metis-science/metis-client/blob/master/CONTRIBUTING.md). Note, that our [changelog](https://github.com/metis-science/metis-client/blob/master/CHANGELOG.md) is maintained fully automatically via [GitHub actions](https://github.com/metis-science/metis-client/tree/master/.github/workflows). An approved release is also automatically uploaded to PyPI. Feel free to use these actions in your own repo, just set the correct repo name in the action `.yml` file.


## License

Author Sergey Korolev, Tilde Materials Informatics

Copyright 2023-2024 BASF SE
Copyright 2024-2025 Tilde Materials Informatics

BSD 3-Clause
