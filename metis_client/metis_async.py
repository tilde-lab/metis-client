"""Main Metis API async client"""

import sys
from types import TracebackType
from typing import Optional, Type

import aiohttp
from aiohttp import ClientSession, ClientTimeout, TraceConfig
from aiohttp.hdrs import USER_AGENT
from aiohttp.typedefs import LooseHeaders, StrOrURL
from yarl import URL

from .client import MetisClient
from .const import DEFAULT_USER_AGENT
from .models import BaseAuthenticator, MetisBase
from .namespaces.root import MetisRootNamespace
from .namespaces.stream import MetisStreamNamespace
from .namespaces.v0 import MetisV0Namespace

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import List
else:  # pragma: no cover
    List = list

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import NotRequired, TypedDict, Unpack
else:  # pragma: no cover
    from typing import NotRequired, TypedDict, Unpack


class MetisAPIKwargs(TypedDict):
    "MetisAPI init kwargs"
    auth: BaseAuthenticator
    headers: NotRequired[LooseHeaders]
    timeout: NotRequired[int]
    client_name: NotRequired[str]
    trace_configs: NotRequired[List[TraceConfig]]


class MetisAPIAsync(MetisBase):
    """Main Metis API async client"""

    _close_session = False
    _session: aiohttp.ClientSession

    def __init__(
        self,
        base_url: StrOrURL,
        session: Optional[ClientSession] = None,
        **opts: Unpack[MetisAPIKwargs],
    ):
        """
        Initialize async Metis client.

        **Arguments**:

        `bese_url`
        URL of Metis BFF server. `str` or `yarl.URL`.

        `session` (Optional)
        `aiohttp.ClientSession` to be used by this package.
        If you do not pass one, one will be created for you.

        `headers` (Optional)
        Optional dictionary of always sent headers. Used if `session` is omitted.

        `timeout` (Optional)
        Optional integer of global timeout in seconds or `aiohttp.ClientTimeout`.
        Used if `session` is omitted.

        `client_name` (Optional)
        Optional string for user agent.
        Used if `session` is omitted.
        """
        headers = opts.get("headers")
        if session is None:
            timeout = opts.get("timeout")
            session = aiohttp.ClientSession(
                timeout=timeout
                if isinstance(timeout, ClientTimeout)
                else ClientTimeout(total=timeout),
                headers=headers,
                trace_configs=opts.get("trace_configs"),
            )
            session.headers[USER_AGENT] = opts.get("client_name", DEFAULT_USER_AGENT)
            self._close_session = True
        self._session = session

        base_url = URL(base_url)
        if not base_url.is_absolute():
            raise TypeError("Base URL should be absolute")
        client = MetisClient(session, base_url, opts["auth"])
        self._ns_root = MetisRootNamespace(client, base_url)

    @property
    def v0(self) -> MetisV0Namespace:  # pylint: disable=invalid-name
        """Property to access the v0 namespace."""
        return self._ns_root.v0

    @property
    def stream(self) -> MetisStreamNamespace:
        """Property to access the stream namespace."""
        return self._ns_root.stream

    async def __aenter__(self) -> "MetisAPIAsync":
        """Async enter."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    async def close(self) -> None:
        "Close stream and http session"
        self.stream.close()
        if self._session and self._close_session:
            await self._session.close()
