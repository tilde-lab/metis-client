"""v0 namespace"""

from .base import BaseNamespace
from .v0_auth import MetisV0AuthNamespace
from .v0_calculations import MetisV0CalculationsNamespace
from .v0_collections import MetisV0CollectionsNamespace
from .v0_datasources import MetisV0DatasourcesNamespace


class MetisV0Namespace(BaseNamespace):
    """v0 namespace"""

    def __post_init__(self) -> None:
        self.__ns_auth = MetisV0AuthNamespace(
            self._client, self._base_url / "auth", root=self._root
        )
        self.__ns_calculations = MetisV0CalculationsNamespace(
            self._client, self._base_url / "calculations", root=self._root
        )
        self.__ns_collections = MetisV0CollectionsNamespace(
            self._client, self._base_url / "collections", root=self._root
        )
        self.__ns_datasources = MetisV0DatasourcesNamespace(
            self._client, self._base_url / "datasources", root=self._root
        )

    async def ping(self) -> None:
        "Run ping pong game"
        await self._client.request(url=self._base_url, method="HEAD", json={})

    @property
    def auth(self) -> MetisV0AuthNamespace:
        "Property to access the auth namespace."
        return self.__ns_auth

    @property
    def calculations(self) -> MetisV0CalculationsNamespace:
        "Property to access the calculations namespace."
        return self.__ns_calculations

    @property
    def collections(self) -> MetisV0CollectionsNamespace:
        "Property to access the collections namespace."
        return self.__ns_collections

    @property
    def datasources(self) -> MetisV0DatasourcesNamespace:
        "Property to access the datasources namespace."
        return self.__ns_datasources
