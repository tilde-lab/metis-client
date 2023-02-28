"""Calculations endpoints namespace"""
import sys
from datetime import datetime
from functools import partial
from typing import Optional

from ..dtos import MetisCalculationDTO, MetisRequestIdDTO
from ..helpers import raise_on_metis_error
from ..models import act_and_get_result_from_stream
from .base import BaseNamespace

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Sequence
else:  # pragma: no cover
    from collections.abc import Sequence


class MetisCalculationsNamespace(BaseNamespace):
    """Calculations endpoints namespace"""

    async def cancel_event(self, calc_id: int) -> MetisRequestIdDTO:
        "Cancel calculation"
        async with await self._client.request(
            method="DELETE",
            url=self._base_url / str(calc_id),
            auth_required=True,
        ) as resp:
            return await resp.json()

    async def cancel(self, calc_id: int) -> None:
        "Cancel calculation and wait for result"
        await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.cancel_event, calc_id)
        )

    async def create_event(
        self, data_id: int, engine: str = "dummy"
    ) -> MetisRequestIdDTO:
        "Create calculation"
        async with await self._client.request(
            method="POST",
            url=self._base_url,
            json={"dataId": data_id, "engine": engine},
            auth_required=True,
        ) as resp:
            return await resp.json()

    async def create(
        self, data_id: int, engine: str = "dummy"
    ) -> Optional[MetisCalculationDTO]:
        "Create calculation and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.create_event, data_id, engine)
        )
        if evt["type"] == "calculations":
            data = sorted(
                evt.get("data", {}).get("data", []),
                key=lambda x: x.get("createdAt", datetime.fromordinal(1)),
            )
            return data[-1] if data else None

    @raise_on_metis_error
    async def get_engines(self) -> Sequence[str]:
        "Get supported calculation engines"
        async with await self._client.request(
            method="GET",
            url=self._base_url / "engines",
            auth_required=False,
        ) as resp:
            return await resp.json()

    async def list_event(self) -> MetisRequestIdDTO:
        "List all user's calculations"
        async with await self._client.request(
            method="GET",
            url=self._base_url,
            auth_required=True,
        ) as resp:
            return await resp.json()

    async def list(self) -> Sequence[MetisCalculationDTO]:
        "List all user's calculations and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.list_event)
        )
        if evt["type"] == "calculations":
            return evt.get("data", {}).get("data", [])
        return []  # pragma: no cover
