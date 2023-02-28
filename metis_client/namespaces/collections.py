"""Collections endpoints namespace"""
import sys
from datetime import datetime
from functools import partial
from typing import Optional

from ..dtos import MetisCollectionCreateDTO, MetisCollectionDTO, MetisRequestIdDTO
from ..helpers import raise_on_metis_error
from ..models import act_and_get_result_from_stream
from .base import BaseNamespace

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Sequence
else:  # pragma: no cover
    from collections.abc import Sequence

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import NotRequired, TypedDict, Unpack
else:  # pragma: no cover
    from typing import NotRequired, TypedDict, Unpack


class MetisCollectionsCreateKwargs(TypedDict):
    "MetisCollectionsNamespace.create kwargs"
    description: NotRequired[str]
    data_source_ids: NotRequired[Sequence[int]]
    user_ids: NotRequired[Sequence[int]]


class MetisCollectionsNamespace(BaseNamespace):
    """Collections endpoints namespace"""

    async def create_event(
        self, type_id: int, title: str, **opts: Unpack[MetisCollectionsCreateKwargs]
    ) -> MetisRequestIdDTO:
        "Create collection"
        payload = MetisCollectionCreateDTO(
            title=title,
            typeId=type_id,
            description=opts.get("description", ""),
            dataSources=opts.get("data_source_ids", []),
            users=opts.get("user_ids", []),
        )
        async with await self._client.request(
            method="PUT",
            url=self._base_url,
            json=payload,
            auth_required=True,
        ) as resp:
            return await resp.json()

    async def create(
        self, type_id: int, title: str, **opts: Unpack[MetisCollectionsCreateKwargs]
    ) -> Optional[MetisCollectionDTO]:
        "Create collection and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe,
            partial(self.create_event, type_id, title, **opts),
        )
        if evt["type"] == "collections":
            data = sorted(
                evt.get("data", {}).get("data", []),
                key=lambda x: x.get("createdAt", datetime.fromordinal(1)),
            )
            return data[-1] if data else None

    async def list_event(self) -> MetisRequestIdDTO:
        "List user's collections by criteria"
        async with await self._client.request(
            method="GET",
            url=self._base_url,
            auth_required=True,
        ) as resp:
            return await resp.json()

    @raise_on_metis_error
    async def list(self) -> Sequence[MetisCollectionDTO]:
        "List user's collections by criteria and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.list_event)
        )
        if evt["type"] == "collections":
            return evt.get("data", {}).get("data", [])
        return []  # pragma: no cover

    async def delete_event(self, collection_id: int) -> MetisRequestIdDTO:
        "Remove a collection"
        async with await self._client.request(
            method="DELETE",
            url=self._base_url / str(collection_id),
            auth_required=True,
        ) as resp:
            return await resp.json()

    async def delete(self, collection_id: int) -> None:
        "Remove a collection by id and wait for result"
        await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.delete_event, collection_id)
        )
