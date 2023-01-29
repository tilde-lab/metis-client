"""Calculations endpoints namespace"""
from ..models.resp import MetisRequestIdModel
from .base import BaseNamespace


# pylint: disable=too-few-public-methods
class MetisCalculationsNamespace(BaseNamespace):
    """Calculations endpoints namespace"""

    async def create(self, data_id: int, engine: str = "dummy"):
        "Create calculation"
        async with await self._client.request(
            method="POST",
            url=self._base_url,
            json={"dataId": data_id, "engine": engine},
            auth_required=True,
        ) as resp:
            result = await resp.json()
            return MetisRequestIdModel.from_dto(result)
