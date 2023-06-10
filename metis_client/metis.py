"""Metis API synchronous client"""

import asyncio
import sys
from functools import partial
from typing import Any, Literal, Optional, Sequence, TypeVar, Union, cast

from aiohttp.typedefs import StrOrURL
from asgiref.sync import async_to_sync

from metis_client.dtos.datasource import MetisDataSourceDTO

from .metis_async import MetisAPIAsync, MetisAPIKwargs
from .models.base import MetisBase
from .namespaces.v0_calculations import MetisCalculationOnProgressT
from .namespaces.v0_collections import MetisCollectionsCreateKwargs

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
TimeoutType = Union[float, Literal[False], None]


# pylint: disable=too-few-public-methods
class MetisNamespaceSyncBase:
    "Base for synchronous namespaces"
    _client_getter: AsyncClientGetter
    _default_timeout: TimeoutType

    def __init__(
        self, client_getter: AsyncClientGetter, default_timeout: TimeoutType = False
    ):
        self._client_getter = client_getter
        self._default_timeout = default_timeout

    def _get_timeout(self, timeout: TimeoutType) -> Optional[float]:
        "Normalize timeout value"
        if timeout is False:
            return None
        if timeout is not None:
            return timeout
        if not self._default_timeout:
            return None
        return self._default_timeout


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
        timeout = self._get_timeout(cast(TimeoutType, kwargs.get("timeout", None)))
        # pylint: disable=protected-access
        async with self._client_getter() as client:
            return await asyncio.wait_for(func(self, client, *args, **kwargs), timeout)

    return cast(Any, async_to_sync(inner))


class MetisCalculationsNamespaceSync(MetisNamespaceSyncBase):
    """Calculations endpoints namespace"""

    @to_sync_with_metis_client
    async def supported(self, client: MetisAPIAsync):
        "Get supported calculation engines"
        return await client.calculations.supported()


class MetisV0AuthNamespaceSync(MetisNamespaceSyncBase):
    """Authentication endpoints namespace"""

    # pylint: disable=unused-argument

    @to_sync_with_metis_client
    async def login(
        self,
        client: MetisAPIAsync,
        email: str,
        password: str,
        timeout: TimeoutType = None,
    ):
        "Login"
        return await client.v0.auth.login(email, password)

    @to_sync_with_metis_client
    async def whoami(self, client: MetisAPIAsync, timeout: TimeoutType = None):
        "Get self info"
        return await client.v0.auth.whoami()


class MetisV0DatasourcesNamespaceSync(MetisNamespaceSyncBase):
    """Datasources endpoints namespace"""

    # pylint: disable=unused-argument

    @to_sync_with_metis_client
    async def create(
        self,
        client: MetisAPIAsync,
        content: str,
        fmt: Optional[str] = None,
        name: Optional[str] = None,
        timeout: TimeoutType = None,
    ):
        "Create data source and wait for the result"
        return await client.v0.datasources.create(content, fmt, name)

    @to_sync_with_metis_client
    async def delete(
        self, client: MetisAPIAsync, data_id: int, timeout: TimeoutType = None
    ):
        "Delete data source by id and wait for the result"
        return await client.v0.datasources.delete(data_id)

    @to_sync_with_metis_client
    async def list(self, client: MetisAPIAsync, timeout: TimeoutType = None):
        "List data sources and wait for the result"
        return await client.v0.datasources.list()

    @to_sync_with_metis_client
    async def get(
        self, client: MetisAPIAsync, data_id: int, timeout: TimeoutType = None
    ) -> Optional[MetisDataSourceDTO]:
        "Get data source by id"
        return await client.v0.datasources.get(data_id)

    @to_sync_with_metis_client
    async def get_parents(
        self, client: MetisAPIAsync, data_id: int, timeout: TimeoutType = None
    ) -> Sequence[MetisDataSourceDTO]:
        "Get parent data sources by id"
        return await client.v0.datasources.get_parents(data_id)

    @to_sync_with_metis_client
    async def get_children(
        self, client: MetisAPIAsync, data_id: int, timeout: TimeoutType = None
    ) -> Sequence[MetisDataSourceDTO]:
        "Get children data sources by id"
        return await client.v0.datasources.get_children(data_id)

    @to_sync_with_metis_client
    async def get_content(
        self, client: MetisAPIAsync, data_id: int, timeout: TimeoutType = None
    ):
        "Get data source by id"
        return await client.v0.datasources.get_content(data_id)


class MetisV0CalculationsNamespaceSync(MetisNamespaceSyncBase):
    """Calculations endpoints namespace"""

    # pylint: disable=unused-argument

    @to_sync_with_metis_client
    async def cancel(
        self, client: MetisAPIAsync, calc_id: int, timeout: TimeoutType = None
    ):
        "Cancel calculation and wait for the result"
        return await client.v0.calculations.cancel(calc_id)

    @to_sync_with_metis_client
    async def create(
        self,
        client: MetisAPIAsync,
        data_id: int,
        engine: str = "dummy",
        input: Optional[str] = None,  # pylint: disable=redefined-builtin
        timeout: TimeoutType = None,
    ):
        "Create calculation and wait for the result"
        return await client.v0.calculations.create(data_id, engine, input)

    @to_sync_with_metis_client
    async def get_results(
        self,
        client: MetisAPIAsync,
        calc_id: int,
        on_progress: Optional[MetisCalculationOnProgressT] = None,
        timeout: TimeoutType = None,
    ):
        "Waits for the end of the calculation and returns the results"
        return await client.v0.calculations.get_results(calc_id, on_progress)

    @to_sync_with_metis_client
    async def create_get_results(
        self,
        client: MetisAPIAsync,
        data_id: int,
        engine: str = "dummy",
        input: Optional[str] = None,  # pylint: disable=redefined-builtin
        on_progress: Optional[MetisCalculationOnProgressT] = None,
        timeout: TimeoutType = None,
    ):
        "Create calculation, wait done and get results"
        return await client.v0.calculations.create_get_results(
            data_id, engine, input, on_progress
        )

    @to_sync_with_metis_client
    async def get_engines(self, client: MetisAPIAsync, timeout: TimeoutType = None):
        "Get supported calculation engines"
        return await client.v0.calculations.get_engines()

    @to_sync_with_metis_client
    async def list(self, client: MetisAPIAsync, timeout: TimeoutType = None):
        "List all user's calculations and wait for the result"
        return await client.v0.calculations.list()

    @to_sync_with_metis_client
    async def get(
        self, client: MetisAPIAsync, calc_id: int, timeout: TimeoutType = None
    ):
        "Get calculation by id"
        return await client.v0.calculations.get(calc_id)


class MetisV0CollectionsNamespaceSync(MetisNamespaceSyncBase):
    """Collections endpoints namespace"""

    # pylint: disable=unused-argument

    @to_sync_with_metis_client
    async def create(
        self,
        client: MetisAPIAsync,
        type_id: int,
        title: str,
        timeout: TimeoutType = None,
        **opts: Unpack[MetisCollectionsCreateKwargs],
    ):
        "Create collection and wait for the result"
        return await client.v0.collections.create(type_id, title, **opts)

    @to_sync_with_metis_client
    async def list(self, client: MetisAPIAsync, timeout: TimeoutType = None):
        "List user's collections by criteria and wait for the result"
        return await client.v0.collections.list()

    @to_sync_with_metis_client
    async def delete(
        self, client: MetisAPIAsync, collection_id: int, timeout: TimeoutType = None
    ):
        "Remove a collection by id and wait for the result"
        return await client.v0.collections.delete(collection_id)


# pylint: disable=too-few-public-methods
class MetisV0NamespaceSync(MetisNamespaceSyncBase):
    """v0 namespace"""

    def __init__(
        self, client_getter: AsyncClientGetter, default_timeout: Optional[float] = False
    ):
        super().__init__(client_getter, default_timeout)
        self.auth = MetisV0AuthNamespaceSync(client_getter, default_timeout)
        self.calculations = MetisV0CalculationsNamespaceSync(
            client_getter, default_timeout
        )
        self.collections = MetisV0CollectionsNamespaceSync(
            client_getter, default_timeout
        )
        self.datasources = MetisV0DatasourcesNamespaceSync(
            client_getter, default_timeout
        )


class MetisAPI(MetisBase):
    """Metis API synchronous client"""

    def __init__(
        self,
        base_url: StrOrURL,
        **opts: Unpack[MetisAPIKwargs],
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
        Optional float timeout in seconds. None if no timeout. False if not set.
        Used as `aiohttp` timeout if `session` is omitted.
        Used as global timeout for SSE responses.

        `client_name` (Optional)
        Optional string for user agent.
        """
        timeout = opts.get("timeout", None)
        self._ns_calculations = MetisCalculationsNamespaceSync(
            partial(MetisAPIAsync, base_url, **opts), timeout
        )
        self._ns_v0 = MetisV0NamespaceSync(
            partial(MetisAPIAsync, base_url, **opts), timeout
        )

    @property
    def calculations(
        self,
    ) -> MetisCalculationsNamespaceSync:  # pylint: disable=invalid-name
        """Property to access the calculations namespace."""
        return self._ns_calculations

    @property
    def v0(self) -> MetisV0NamespaceSync:  # pylint: disable=invalid-name
        """Property to access the v0 namespace."""
        return self._ns_v0
