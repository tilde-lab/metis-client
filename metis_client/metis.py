"""Metis API synchronous client"""

import sys
from functools import partial
from typing import Any, TypeVar, cast

from aiohttp.typedefs import StrOrURL
from asgiref.sync import async_to_sync

from .metis_async import MetisAPIAsync, MetisAPIKwargs
from .models.base import MetisBase
from .namespaces.collections import MetisCollectionsCreateKwargs

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Awaitable, Callable
else:  # pragma: no cover
    from collections.abc import Awaitable, Callable

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import Concatenate, ParamSpec, Unpack
else:  # pragma: no cover
    from typing import Concatenate, ParamSpec, Unpack

AsyncClientGetter = Callable[[], MetisAPIAsync]
ReturnT_co = TypeVar("ReturnT_co", covariant=True)
ParamT = ParamSpec("ParamT")


# pylint: disable=too-few-public-methods
class MetisNamespaceSyncBase:
    "Base for synchronous namespaces"
    _client_getter: AsyncClientGetter

    def __init__(self, client_getter: AsyncClientGetter):
        self._client_getter = client_getter


def to_sync_with_metis_client(
    func: Callable[Concatenate[Any, MetisAPIAsync, ParamT], Awaitable[ReturnT_co]]
) -> Callable[Concatenate[Any, ParamT], ReturnT_co]:
    """
    Wraps async MetisNamespaceSync's method.
    - start MetisAPIAsync client,
    - pass it to the method as first argument after Self,
    - close client
    - wrap all with async_to_sync converter
    """

    async def inner(
        self: MetisNamespaceSyncBase, *args: ParamT.args, **kwargs: ParamT.kwargs
    ) -> ReturnT_co:
        # pylint: disable=protected-access
        async with self._client_getter() as client:
            return await func(self, client, *args, **kwargs)

    return cast(Any, async_to_sync(inner))


class MetisAuthNamespaceSync(MetisNamespaceSyncBase):
    """Authentication endpoints namespace"""

    @to_sync_with_metis_client
    async def login(self, client: MetisAPIAsync, email: str, password: str):
        "Login"
        return await client.v0.auth.login(email, password)

    @to_sync_with_metis_client
    async def whoami(self, client: MetisAPIAsync):
        "Get self info"
        return await client.v0.auth.whoami()


class MetisDatasourcesNamespaceSync(MetisNamespaceSyncBase):
    """Datasources endpoints namespace"""

    @to_sync_with_metis_client
    async def create(self, client: MetisAPIAsync, content: str):
        "Create data source and wait for result"
        return await client.v0.datasources.create(content)

    @to_sync_with_metis_client
    async def delete(self, client: MetisAPIAsync, data_id: int):
        "Delete data source by id and wait for result"
        return await client.v0.datasources.delete(data_id)

    @to_sync_with_metis_client
    async def list(self, client: MetisAPIAsync):
        "List data sources and wait for result"
        return await client.v0.datasources.list()

    @to_sync_with_metis_client
    async def get(self, client: MetisAPIAsync, data_id: int):
        "Get data source by id"
        return await client.v0.datasources.get(data_id)


class MetisCalculationsNamespaceSync(MetisNamespaceSyncBase):
    """Calculations endpoints namespace"""

    @to_sync_with_metis_client
    async def cancel(self, client: MetisAPIAsync, calc_id: int):
        "Cancel calculation and wait for result"
        return await client.v0.calculations.cancel(calc_id)

    @to_sync_with_metis_client
    async def create(self, client: MetisAPIAsync, data_id: int, engine: str = "dummy"):
        "Create calculation and wait for result"
        return await client.v0.calculations.create(data_id, engine)

    @to_sync_with_metis_client
    async def get_engines(self, client: MetisAPIAsync):
        "Get supported calculation engines"
        return await client.v0.calculations.get_engines()

    @to_sync_with_metis_client
    async def list(self, client: MetisAPIAsync):
        "List all user's calculations and wait for result"
        return await client.v0.calculations.list()


class MetisCollectionsNamespaceSync(MetisNamespaceSyncBase):
    """Collections endpoints namespace"""

    @to_sync_with_metis_client
    async def create(
        self,
        client: MetisAPIAsync,
        type_id: int,
        title: str,
        **opts: Unpack[MetisCollectionsCreateKwargs],
    ):
        "Create collection and wait for result"
        return await client.v0.collections.create(type_id, title, **opts)

    @to_sync_with_metis_client
    async def list(self, client: MetisAPIAsync):
        "List user's collections by criteria and wait for result"
        return await client.v0.collections.list()

    @to_sync_with_metis_client
    async def delete(self, client: MetisAPIAsync, collection_id: int):
        "Remove a collection by id and wait for result"
        return await client.v0.collections.delete(collection_id)


# pylint: disable=too-few-public-methods
class MetisV0NamespaceSync(MetisNamespaceSyncBase):
    """v0 namespace"""

    def __init__(self, client_getter: AsyncClientGetter):
        super().__init__(client_getter)
        self.auth = MetisAuthNamespaceSync(client_getter)
        self.calculations = MetisCalculationsNamespaceSync(client_getter)
        self.collections = MetisCollectionsNamespaceSync(client_getter)
        self.datasources = MetisDatasourcesNamespaceSync(client_getter)


class MetisAPI(MetisBase):
    """Metis API synchronous client"""

    def __init__(
        self, base_url: StrOrURL, **opts: Unpack[MetisAPIKwargs]
    ):  # pylint: disable=too-many-arguments
        """
        Initialize sync Metis client.
        Sync client is a tiny wrapper over full async client.

        **Arguments**:

        `bese_url`
        URL of Metis BFF server. `str` or `yarl.URL`.

        `headers` (Optional)
        Optional dictionary of always sent headers. Used if `session` is omitted.

        `timeout` (Optional)
        Optional integer of global timeout in seconds or `aiohttp.ClientTimeout`.
        Used if `session` is omitted.

        `client_name` (Optional)
        Optional string for user agent.
        """
        self._ns_v0 = MetisV0NamespaceSync(partial(MetisAPIAsync, base_url, **opts))

    @property
    def v0(self) -> MetisV0NamespaceSync:  # pylint: disable=invalid-name
        """Property to access the v0 namespace."""
        return self._ns_v0
