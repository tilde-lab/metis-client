"""Authentication endpoints namespace"""

from ..dtos import MetisAuthCredentialsRequestDTO, MetisUserDTO
from ..helpers import dict_dt_from_dt_str, raise_on_metis_error
from .base import BaseNamespace


class MetisAuthNamespace(BaseNamespace):
    """Authentication endpoints namespace"""

    @raise_on_metis_error
    async def login(self, email: str, password: str) -> bool:
        "Login"
        payload = MetisAuthCredentialsRequestDTO(email=email, password=password)
        async with self._client.request(
            method="POST",
            url=self._base_url,
            json=payload,
        ) as resp:
            return resp.ok

    @raise_on_metis_error
    async def whoami(self) -> MetisUserDTO:
        "Get self info"
        async with self._client.request(
            url=self._base_url,
            auth_required=self._auth_required,
        ) as resp:
            return dict_dt_from_dt_str(await resp.json())
