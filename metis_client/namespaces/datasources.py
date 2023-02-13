"""Datasources endpoints namespace"""

from functools import partial
from typing import Optional, Sequence, Union

from ..models.datasource import MetisDataSourceContentOnlyModel, MetisDataSourceModel
from ..models.error import MetisErrorModel
from ..models.event import MetisDataSourcesEventModel, MetisErrorEventModel
from ..models.pubsub import act_and_get_result_from_stream
from ..models.resp import MetisRequestIdModel
from .base import BaseNamespace


class MetisDatasourcesNamespace(BaseNamespace):
    """Datasources endpoints namespace"""

    async def create_event(self, content: str) -> MetisRequestIdModel:
        "Create data source"
        async with self._client.request(
            method="POST",
            url=self._base_url,
            json={"content": content},
            auth_required=True,
        ) as resp:
            return MetisRequestIdModel.from_dto(await resp.json())

    async def create(
        self, content: str
    ) -> Union[MetisDataSourceModel, MetisErrorModel, None]:
        "Create data source and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.create_event, content)
        )
        if MetisErrorEventModel.guard(evt) and evt.errors:
            return evt.errors[-1]
        if MetisDataSourcesEventModel.guard(evt):
            data = sorted(evt.data, key=lambda x: x.created_at)
            return data[-1] if data else None

    async def delete_event(self, data_id: int) -> MetisRequestIdModel:
        "Delete data source by id"
        async with self._client.request(
            method="DELETE",
            url=self._base_url / str(data_id),
            auth_required=True,
        ) as resp:
            return MetisRequestIdModel.from_dto(await resp.json())

    async def delete(self, data_id: int) -> Optional[MetisErrorModel]:
        "Delete data source by id and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.delete_event, data_id)
        )
        if MetisErrorEventModel.guard(evt) and evt.errors:
            return evt.errors[-1]

    async def list_event(self) -> MetisRequestIdModel:
        "List data sources"
        async with self._client.request(
            method="GET",
            url=self._base_url,
            auth_required=True,
        ) as resp:
            return MetisRequestIdModel.from_dto(await resp.json())

    async def list(
        self,
    ) -> Union[MetisErrorModel, Sequence[MetisDataSourceModel], None]:
        "List data sources and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.list_event)
        )
        if MetisErrorEventModel.guard(evt) and evt.errors:
            return evt.errors[-1]
        if MetisDataSourcesEventModel.guard(evt):
            return evt.data

    async def get(self, data_id: int) -> MetisDataSourceContentOnlyModel:
        "Get data source by id"
        async with self._client.request(
            method="GET",
            url=self._base_url / str(data_id),
            auth_required=True,
        ) as resp:
            return MetisDataSourceContentOnlyModel.from_dto(await resp.json())
