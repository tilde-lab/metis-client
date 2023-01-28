"""Datasources endpoints namespace"""

from ..models.resp import MetisRequestIdModel
from .base import BaseNamespace


# pylint: disable=too-few-public-methods
class MetisDatasourcesNamespace(BaseNamespace):
    """Datasources endpoints namespace"""

    async def list(self):
        "List data sources"
        async with self._client.request(
            method="GET",
            url=self._base_url,
            auth_required=True,
        ) as resp:
            return MetisRequestIdModel.from_dto(await resp.json())

    async def create(self, content: str):
        "Create data source"
        async with self._client.request(
            method="POST",
            url=self._base_url,
            json={"content": content},
            auth_required=True,
        ) as resp:
            return MetisRequestIdModel.from_dto(await resp.json())

    # async def get(self, data_id: int):
    #     "Get data source by id"
    #     async with self._client.request(
    #         method="GET",
    #         url=self._base_url / str(data_id),
    #         auth_required=True,
    #     ) as resp:
    #         # print(await resp.json())
    #         # WTF THIS IS BROKEN
    #         return MetisDataSourceModel.from_dto(await resp.json())

    async def delete(self, data_id: int):
        "Delete data source by id"
        async with self._client.request(
            method="DELETE",
            url=self._base_url / str(data_id),
            auth_required=True,
        ) as resp:
            return MetisRequestIdModel.from_dto(await resp.json())
