"""Collections endpoints namespace"""

from datetime import datetime
from functools import partial
from typing import Optional

from ..compat import NotRequired, Sequence, TypedDict, Unpack
from ..dtos import (
    MetisCollectionCreateDTO,
    MetisCollectionDTO,
    MetisCollectionVisibility,
    MetisRequestIdDTO,
)
from ..helpers import metis_json_decoder, raise_on_metis_error
from ..models import act_and_get_result_from_stream
from .base import BaseNamespace


class MetisCollectionsCreateKwargs(TypedDict):
    "MetisV0CollectionsNamespace.create kwargs"
    id: NotRequired[int]
    description: NotRequired[str]
    data_source_ids: NotRequired[Sequence[int]]
    user_ids: NotRequired[Sequence[int]]
    visibility: NotRequired[MetisCollectionVisibility]


class MetisV0CollectionsNamespace(BaseNamespace):
    """Collections endpoints namespace"""

    async def create_event(
        self, type_id: int, title: str, **opts: Unpack[MetisCollectionsCreateKwargs]
    ) -> MetisRequestIdDTO:
        "Create or edit the collection"
        payload = MetisCollectionCreateDTO(
            title=title,
            type_id=type_id,
            description=opts.get("description", ""),
            data_sources=opts.get("data_source_ids", []),
            users=opts.get("user_ids", []),
            visibility=opts.get("visibility", "private"),
        )

        if "id" in opts:
            payload["id"] = opts["id"]

        async with await self._client.request(
            method="PUT",
            url=self._base_url,
            json=payload,
            auth_required=True,
        ) as resp:
            return await resp.json(loads=metis_json_decoder)

    async def create(
        self, type_id: int, title: str, **opts: Unpack[MetisCollectionsCreateKwargs]
    ) -> Optional[MetisCollectionDTO]:
        "Create or edit the collection and wait for the result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe,
            partial(self.create_event, type_id, title, **opts),
        )
        if evt["type"] == "collections":
            data = sorted(
                evt.get("data", {}).get("data", []),
                key=lambda x: x.get("created_at", datetime.fromordinal(1)),
            )
            return data[-1] if data else None

    async def list_event(self) -> MetisRequestIdDTO:
        "List user's collections by criteria"
        async with await self._client.request(
            method="GET",
            url=self._base_url,
            auth_required=True,
        ) as resp:
            return await resp.json(loads=metis_json_decoder)

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
            return await resp.json(loads=metis_json_decoder)

    async def delete(self, collection_id: int) -> None:
        "Remove a collection by id and wait for result"
        await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.delete_event, collection_id)
        )
