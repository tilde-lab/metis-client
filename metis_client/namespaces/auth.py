from .base import BaseNamespace
from ..models.auth import MetisWhoAmIModel, MetisAuthCredentialsModel
from ..models.error import MetisErrorModel
from ..exc import MetisAuthenticationException


class MetisAuthNamespace(BaseNamespace):
    async def login(self, email: str, password: str) -> bool | MetisErrorModel:
        payload = MetisAuthCredentialsModel(email, password).to_request()
        try:
            async with self._client.request(
                method="POST",
                url=self._base_url,
                json=payload,
            ) as r:
                return r.ok
        except MetisAuthenticationException as err:
            return MetisErrorModel(status=err.status, message=err.error)

    async def whoami(self) -> MetisWhoAmIModel:
        """
        Get self info
        """
        async with self._client.request(
            url=self._base_url,
            auth_requered=self._auth_requered,
        ) as r:
            return MetisWhoAmIModel.from_response(await r.json())
