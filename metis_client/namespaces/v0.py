"""v0 namespace"""

from .auth import MetisAuthNamespace
from .base import BaseNamespace
from .calculations import MetisCalculationsNamespace
from .collections import MetisCollectionsNamespace
from .datasources import MetisDatasourcesNamespace


class MetisV0Namespace(BaseNamespace):
    """v0 namespace"""

    def __post_init__(self) -> None:
        self.__ns_auth = MetisAuthNamespace(
            self._client, self._base_url / "auth", root=self._root
        )
        self.__ns_calculations = MetisCalculationsNamespace(
            self._client, self._base_url / "calculations", root=self._root
        )
        self.__ns_collections = MetisCollectionsNamespace(
            self._client, self._base_url / "collections", root=self._root
        )
        self.__ns_datasources = MetisDatasourcesNamespace(
            self._client, self._base_url / "datasources", root=self._root
        )

    async def ping(self) -> None:
        "Run ping pong game"
        await self._client.request(url=self._base_url, method="HEAD", json={})

    @property
    def auth(self) -> MetisAuthNamespace:
        "Property to access the auth namespace."
        return self.__ns_auth

    @property
    def calculations(self) -> MetisCalculationsNamespace:
        "Property to access the calculations namespace."
        return self.__ns_calculations

    @property
    def collections(self) -> MetisCollectionsNamespace:
        "Property to access the collections namespace."
        return self.__ns_collections

    @property
    def datasources(self) -> MetisDatasourcesNamespace:
        "Property to access the datasources namespace."
        return self.__ns_datasources
