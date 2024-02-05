"""Calculations endpoints namespace"""

from ..compat import Sequence
from ..helpers import metis_json_decoder, raise_on_metis_error
from .base import BaseNamespace


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
            return await resp.json(loads=metis_json_decoder)
