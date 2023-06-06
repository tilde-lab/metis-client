"""Calculations endpoints namespace"""
import sys

from ..helpers import raise_on_metis_error
from .base import BaseNamespace

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Sequence
else:  # pragma: no cover
    from collections.abc import Sequence


class MetisCalculationsNamespace(BaseNamespace):
    """Calculations endpoints namespace"""

    @raise_on_metis_error
    async def supported(self) -> Sequence[str]:
        "Get supported calculation engines"
        async with await self._client.request(
            method="GET",
            url=self._base_url / "supported",
            auth_required=False,
        ) as resp:
            return await resp.json()
