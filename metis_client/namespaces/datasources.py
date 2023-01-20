from .base import BaseNamespace
from ..models.resp import MetisRequestIdModel


class MetisDatasourcesNamespace(BaseNamespace):
    async def create(self, content: str):
        async with self._client.request(
            method="POST",
            url=self._base_url,
            json={"content": content},
            auth_requered=True,
        ) as r:
            return MetisRequestIdModel.from_response(await r.json())
