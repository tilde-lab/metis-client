"""Authentication endpoints namespace"""

from typing import Union

from ..exc import MetisAuthenticationException
from ..models.auth import MetisAuthCredentialsModel
from ..models.error import MetisErrorModel
from ..models.user import MetisUserModel
from .base import BaseNamespace


class MetisAuthNamespace(BaseNamespace):
    """Authentication endpoints namespace"""

    async def login(self, email: str, password: str) -> Union[bool, MetisErrorModel]:
        "Login"
        payload = MetisAuthCredentialsModel(email, password).to_dto()
        try:
            async with self._client.request(
                method="POST",
                url=self._base_url,
                json=payload,
            ) as resp:
                return resp.ok
        except MetisAuthenticationException as err:
            return MetisErrorModel(status=err.status, message=err.error or str(err))

    async def whoami(self) -> MetisUserModel:
        "Get self info"
        async with self._client.request(
            url=self._base_url,
            auth_required=self._auth_required,
        ) as resp:
            return MetisUserModel.from_dto(await resp.json())
