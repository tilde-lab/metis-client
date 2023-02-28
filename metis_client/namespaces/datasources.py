"""Datasources endpoints namespace"""

import sys
from datetime import datetime
from functools import partial
from typing import Optional

from ..dtos import MetisDataSourceContentOnlyDTO, MetisDataSourceDTO, MetisRequestIdDTO
from ..helpers import raise_on_metis_error
from ..models import act_and_get_result_from_stream
from .base import BaseNamespace

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Sequence
else:  # pragma: no cover
    from collections.abc import Sequence


class MetisDatasourcesNamespace(BaseNamespace):
    """Datasources endpoints namespace"""

    async def create_event(self, content: str) -> MetisRequestIdDTO:
        "Create data source"
        async with self._client.request(
            method="POST",
            url=self._base_url,
            json={"content": content},
            auth_required=True,
        ) as resp:
            return await resp.json()

    async def create(self, content: str) -> Optional[MetisDataSourceDTO]:
        "Create data source and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.create_event, content)
        )
        if evt["type"] == "datasources":
            data = sorted(
                evt.get("data", {}).get("data", []),
                key=lambda x: x.get("createdAt", datetime.fromordinal(1)),
            )
            return data[-1] if data else None

    async def delete_event(self, data_id: int) -> MetisRequestIdDTO:
        "Delete data source by id"
        async with self._client.request(
            method="DELETE",
            url=self._base_url / str(data_id),
            auth_required=True,
        ) as resp:
            return await resp.json()

    async def delete(self, data_id: int) -> None:
        "Delete data source by id and wait for result"
        await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.delete_event, data_id)
        )

    async def list_event(self) -> MetisRequestIdDTO:
        "List data sources"
        async with self._client.request(
            method="GET",
            url=self._base_url,
            auth_required=True,
        ) as resp:
            return await resp.json()

    async def list(self) -> Sequence[MetisDataSourceDTO]:
        "List data sources and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.list_event)
        )
        if evt["type"] == "datasources":
            return evt.get("data", {}).get("data", [])
        return []  # pragma: no cover

    @raise_on_metis_error
    async def get(self, data_id: int) -> MetisDataSourceContentOnlyDTO:
        "Get data source by id"
        async with self._client.request(
            method="GET",
            url=self._base_url / str(data_id),
            auth_required=True,
        ) as resp:
            return await resp.json()
