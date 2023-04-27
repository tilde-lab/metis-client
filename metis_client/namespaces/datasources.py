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

    async def create_event(
        self, content: str, fmt: Optional[str] = None, name: Optional[str] = None
    ) -> MetisRequestIdDTO:
        "Create data source"
        async with self._client.request(
            method="POST",
            url=self._base_url,
            json={"content": content, "fmt": fmt, "name": name},
            auth_required=True,
        ) as resp:
            return await resp.json()

    async def create(
        self, content: str, fmt: Optional[str] = None, name: Optional[str] = None
    ) -> Optional[MetisDataSourceDTO]:
        "Create data source and wait for the result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.create_event, content, fmt, name)
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
        "Delete data source by id and wait for the result"
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
        "List data sources and wait for the result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.list_event)
        )
        if evt["type"] == "datasources":
            return evt.get("data", {}).get("data", [])
        return []  # pragma: no cover

    async def get(self, data_id: int) -> Optional[MetisDataSourceDTO]:
        "Get data source by id"
        data = list(filter(lambda x: x["id"] == data_id, await self.list()))
        return data[-1] if data else None

    async def get_parents(self, data_id: int) -> Sequence[MetisDataSourceDTO]:
        "Get parent data sources by id"
        return list(
            filter(lambda x: data_id in x.get("children", []), await self.list())
        )

    async def get_children(self, data_id: int) -> Sequence[MetisDataSourceDTO]:
        "Get children data sources by id"
        return list(
            filter(lambda x: data_id in x.get("parents", []), await self.list())
        )

    @raise_on_metis_error
    async def get_content(self, data_id: int) -> MetisDataSourceContentOnlyDTO:
        "Get data source by id"
        async with self._client.request(
            method="GET",
            url=self._base_url / str(data_id),
            auth_required=True,
        ) as resp:
            return await resp.json()
