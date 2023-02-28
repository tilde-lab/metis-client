# Metis API client

![PyPI](https://img.shields.io/pypi/v/metis_client.svg?style=flat)

<p align="center"><img src="https://github.com/tilde-lab/metis.science/blob/master/src/assets/img/metis.svg" width="300" height="300" /></p>

This library allows for programmatic interactions with the [Metis infrastructure](https://metis.science).

## Installation

`pip install metis_client`

## Usage

There are two client flavors - asyncronous `asyncio` client
and simplified synchronous client.

### Asynchronous client

There is a asynchronous client `MetisAPIAsync`. Example of usage:

```python
from metis_client import MetisAPIAsync, MetisTokenAuth

async def main():
    async with MetisAPIAsync(API_URL, auth=MetisTokenAuth("admin@test.com")) as client:
        print(await client.v0.auth.whoami())
        data = await client.v0.datasources.create(content)
        calc = await client.v0.calculations.create(data["id"])
        print(calc)

        # There is also a low level interface
        from metis_client.models import MetisDataSourcesEventModel, MetisCalculationsEventModel
        async with client.stream.subscribe() as sub:
            req = await client.v0.datasources.create_event(content)
            async for msg in sub:
                if msg["type"] == "datasources" and msg.get("data", {}).get(
                    "reqId"
                ) == req.get("reqId"):
                    answer = msg.get("data")
                    break
            if not answer:
                return None

            data_id = sorted(
                answer.get("data", []),
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
```

See `examples` directory for more examples.

### Synchronous client

There is a synchronous client `MetisAPI`. Example of usage:

```python
from metis_client import MetisAPI, MetisTokenAuth

client = MetisAPI(API_URL, auth=MetisTokenAuth("admin@test.com"))
data = client.v0.datasources.create(content)
calc = client.v0.calculations.create(data.get("id"))
print(calc)
```

## License

Author Sergey Korolev, Tilde Materials Informatics

Copyright 2023 BASF SE

BSD 3-Clause
