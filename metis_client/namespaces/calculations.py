"""Calculations endpoints namespace"""
import sys
from datetime import datetime
from functools import partial
from inspect import iscoroutinefunction
from typing import Awaitable, Callable, Optional, Union, cast

from ..dtos import (
    DataSourceType,
    MetisCalculationDTO,
    MetisDataSourceDTO,
    MetisRequestIdDTO,
)
from ..helpers import raise_on_metis_error
from ..models import act_and_get_result_from_stream
from .base import BaseNamespace

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Sequence
else:  # pragma: no cover
    from collections.abc import Sequence


DATA_SOURCE_CALC_RESULT_TYPES = [DataSourceType.PROPERTY, DataSourceType.PATTERN]

MetisCalculationOnProgressT = Callable[
    [MetisCalculationDTO], Union[Optional[bool], Awaitable[Optional[bool]]]
]


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
        self,
        data_id: int,
        engine: str = "dummy",
        input: Optional[str] = None,  # pylint: disable=redefined-builtin
    ) -> MetisRequestIdDTO:
        "Create calculation"
        async with await self._client.request(
            method="POST",
            url=self._base_url,
            json={"dataId": data_id, "engine": engine, "input": input},
            auth_required=True,
        ) as resp:
            return await resp.json()

    async def create(
        self,
        data_id: int,
        engine: str = "dummy",
        input: Optional[str] = None,  # pylint: disable=redefined-builtin
    ) -> Optional[MetisCalculationDTO]:
        "Create calculation and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe,
            partial(self.create_event, data_id, engine, input),
        )
        if evt["type"] == "calculations":
            data = sorted(
                evt.get("data", {}).get("data", []),
                key=lambda x: x.get("createdAt", datetime.fromordinal(1)),
            )
            return data[-1] if data else None

    async def _get_results(
        self,
        calc_getter: Callable[[], Awaitable[Optional[MetisCalculationDTO]]],
        on_progress: Optional[MetisCalculationOnProgressT] = None,
    ) -> Optional[Sequence[MetisDataSourceDTO]]:
        "Waits for the end of the calculation and returns the results"

        def get_new_calc_id(data_id: int, calcs: Sequence[MetisCalculationDTO]):
            """
            The funny part is that when the computation ends,
            we get a data source instead of a calculation.
            """
            for calc in calcs:
                if calc.get("progress", 0) < 100:
                    continue
                data = cast(MetisDataSourceDTO, calc)
                if data_id in data.get("parents", []):
                    return data["id"]
            return None

        def get_calc_from_listing(calc_id: int, calcs: Sequence[MetisCalculationDTO]):
            for calc in calcs:
                if calc_id == calc["id"]:
                    return calc
            return None

        def filter_ds_for_calc(data_id: int, dss: Sequence[MetisDataSourceDTO]):
            return [
                ds
                for ds in dss
                if ds["type"] in DATA_SOURCE_CALC_RESULT_TYPES
                and data_id in ds["parents"]
            ]

        async with self._root.stream.subscribe() as sub:
            target_calc = await calc_getter()
            if not target_calc:
                return  # pragma: no cover
            calc_id = target_calc["id"]
            data_id = target_calc["parent"]
            async for msg in sub:
                if msg["type"] == "calculations":
                    calc_id = get_new_calc_id(data_id, msg["data"]["data"]) or calc_id
                    target_calc = get_calc_from_listing(calc_id, msg["data"]["data"])

                    # run callback if any and exit if needed
                    if target_calc and on_progress:
                        if (
                            await on_progress(target_calc)
                            if iscoroutinefunction(on_progress)
                            else on_progress(target_calc)
                        ) is False:
                            return

                # results
                if msg["type"] == "datasources":
                    results = filter_ds_for_calc(data_id, msg["data"]["data"])
                    # if results or calc is done but no results
                    if results or target_calc is None:
                        return results

    async def get_results(
        self, calc_id: int, on_progress: Optional[MetisCalculationOnProgressT] = None
    ) -> Optional[Sequence[MetisDataSourceDTO]]:
        "Waits for the end of the calculation and returns the results"

        async def get_calc():
            return await self.get(calc_id)

        return await self._get_results(get_calc, on_progress)

    async def create_get_results(
        self,
        data_id: int,
        engine: str = "dummy",
        input: Optional[str] = None,  # pylint: disable=redefined-builtin
        on_progress: Optional[MetisCalculationOnProgressT] = None,
    ) -> Optional[Sequence[MetisDataSourceDTO]]:
        "Create calculation, wait done and get results"

        async def get_calc():
            return await self.create(data_id, engine, input)

        return await self._get_results(get_calc, on_progress)

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

    async def get(self, calc_id: int) -> Optional[MetisCalculationDTO]:
        "Get calculation by id"
        data = list(filter(lambda x: x["id"] == calc_id, await self.list()))
        return data[-1] if data else None
