"""Calculations endpoints namespace"""
from functools import partial
from typing import Sequence, Union

from ..models.calculation import MetisCalculationModel
from ..models.error import MetisErrorModel
from ..models.event import MetisCalculationsEventModel, MetisErrorEventModel
from ..models.pubsub import act_and_get_result_from_stream
from ..models.resp import MetisRequestIdModel
from .base import BaseNamespace


class MetisCalculationsNamespace(BaseNamespace):
    """Calculations endpoints namespace"""

    async def cancel_event(self, calc_id: int) -> MetisRequestIdModel:
        "Cancel calculation"
        async with await self._client.request(
            method="DELETE",
            url=self._base_url / str(calc_id),
            auth_required=True,
        ) as resp:
            result = await resp.json()
            return MetisRequestIdModel.from_dto(result)

    async def cancel(
        self, calc_id: int
    ) -> Union[MetisCalculationModel, MetisErrorModel, None]:
        "Cancel calculation and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.cancel_event, calc_id)
        )
        if MetisErrorEventModel.guard(evt) and evt.errors:
            return evt.errors[-1]
        if MetisCalculationsEventModel.guard(evt):
            for calc in evt.data:
                if calc.id == calc_id:
                    return calc

    async def create_event(
        self, data_id: int, engine: str = "dummy"
    ) -> MetisRequestIdModel:
        "Create calculation"
        async with await self._client.request(
            method="POST",
            url=self._base_url,
            json={"dataId": data_id, "engine": engine},
            auth_required=True,
        ) as resp:
            result = await resp.json()
            return MetisRequestIdModel.from_dto(result)

    async def create(
        self, data_id: int, engine: str = "dummy"
    ) -> Union[MetisCalculationModel, MetisErrorModel, None]:
        "Create calculation and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.create_event, data_id, engine)
        )
        if MetisErrorEventModel.guard(evt) and evt.errors:
            return evt.errors[-1]
        if MetisCalculationsEventModel.guard(evt):
            data = sorted(evt.data, key=lambda x: x.created_at)
            return data[-1] if data else None

    async def get_engines(self) -> Sequence[str]:
        "Get supported calculation engines"
        async with await self._client.request(
            method="GET",
            url=self._base_url / "engines",
            auth_required=False,
        ) as resp:
            return await resp.json()

    async def list_event(self) -> MetisRequestIdModel:
        "List all user's calculations"
        async with await self._client.request(
            method="GET",
            url=self._base_url,
            auth_required=True,
        ) as resp:
            result = await resp.json()
            return MetisRequestIdModel.from_dto(result)

    async def list(
        self,
    ) -> Union[MetisErrorModel, Sequence[MetisCalculationModel], None]:
        "List all user's calculations and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.list_event)
        )
        if MetisErrorEventModel.guard(evt) and evt.errors:
            return evt.errors[-1]
        if MetisCalculationsEventModel.guard(evt):
            return evt.data
