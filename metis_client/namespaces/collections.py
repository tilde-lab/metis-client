"""Collections endpoints namespace"""
from functools import partial
from typing import Optional, Sequence, Union

from typing_extensions import NotRequired, TypedDict, Unpack

from ..models.collection import MetisCollectionCreateDTO, MetisCollectionModel
from ..models.error import MetisErrorModel
from ..models.event import MetisCollectionsEventModel, MetisErrorEventModel
from ..models.pubsub import act_and_get_result_from_stream
from ..models.resp import MetisRequestIdModel
from .base import BaseNamespace


class MetisCollectionsCreateKwargs(TypedDict):
    "MetisCollectionsNamespace.create kwargs"
    description: NotRequired[str]
    data_source_ids: NotRequired[Sequence[int]]
    user_ids: NotRequired[Sequence[int]]


class MetisCollectionsNamespace(BaseNamespace):
    """Collections endpoints namespace"""

    async def create_event(
        self, type_id: int, title: str, **opts: Unpack[MetisCollectionsCreateKwargs]
    ) -> MetisRequestIdModel:
        "Create collection"
        payload = MetisCollectionCreateDTO(
            title=title,
            typeId=type_id,
            description=opts.get("description"),
            dataSources=opts.get("data_source_ids"),
            users=opts.get("user_ids"),
        )
        async with await self._client.request(
            method="PUT",
            url=self._base_url,
            json=payload,
            auth_required=True,
        ) as resp:
            result = await resp.json()
            return MetisRequestIdModel.from_dto(result)

    async def create(
        self, type_id: int, title: str, **opts: Unpack[MetisCollectionsCreateKwargs]
    ) -> Union[MetisCollectionModel, MetisErrorModel, None]:
        "Create collection and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe,
            partial(self.create_event, type_id, title, **opts),
        )
        if MetisErrorEventModel.guard(evt) and evt.errors:
            return evt.errors[-1]
        if MetisCollectionsEventModel.guard(evt):
            data = sorted(evt.data, key=lambda x: x.created_at)
            return data[-1] if data else None

    async def list_event(self) -> MetisRequestIdModel:
        "List user's collections by criteria"
        async with await self._client.request(
            method="GET",
            url=self._base_url,
            auth_required=True,
        ) as resp:
            result = await resp.json()
            return MetisRequestIdModel.from_dto(result)

    async def list(
        self,
    ) -> Union[MetisErrorModel, Sequence[MetisCollectionModel], None]:
        "List user's collections by criteria and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.list_event)
        )
        if MetisErrorEventModel.guard(evt) and evt.errors:
            return evt.errors[-1]
        if MetisCollectionsEventModel.guard(evt):
            return evt.data

    async def delete_event(self, collection_id: int) -> MetisRequestIdModel:
        "Remove a collection"
        async with await self._client.request(
            method="DELETE",
            url=self._base_url / str(collection_id),
            auth_required=True,
        ) as resp:
            result = await resp.json()
            return MetisRequestIdModel.from_dto(result)

    async def delete(self, collection_id: int) -> Optional[MetisErrorModel]:
        "Remove a collection by id and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.delete_event, collection_id)
        )
        if MetisErrorEventModel.guard(evt) and evt.errors:
            return evt.errors[-1]
