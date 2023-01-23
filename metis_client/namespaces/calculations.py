from .base import BaseNamespace
from ..models.resp import MetisRequestIdModel


class MetisCalculationsNamespace(BaseNamespace):

    # TODO test case with error https://github.com/knopki/metis-bff/blob/master/routes/%5Bversion%5D/calculations/index.js#L39
    async def create(self, data_id: int):
        async with await self._client.request(
            method="POST",
            url=self._base_url,
            json={"dataId": data_id},
            auth_required=True,
        ) as r:
            result = await r.json()
            print(result)
            return MetisRequestIdModel.from_response(result)
