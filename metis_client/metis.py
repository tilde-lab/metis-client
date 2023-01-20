from types import TracebackType
from typing import List, Type

import aiohttp
from aiohttp import ClientTimeout, ClientSession, TraceConfig
from aiohttp.hdrs import USER_AGENT
from aiohttp.typedefs import StrOrURL, LooseHeaders

from yarl import URL

from .auth import BaseAuthenticator
from .client import MetisClient
from .const import DEFAULT_USER_AGENT
from .models.base import MetisBase
from .namespaces.root import MetisRootNamespace
from .namespaces.v0 import MetisV0Namespace
from .namespaces.stream import MetisStreamNamespace


class MetisAPI(MetisBase):
    """
    This is the main class to use.
    """

    _close_session = False
    _session: aiohttp.ClientSession

    def __init__(
        self,
        base_url: StrOrURL,
        auth: BaseAuthenticator,
        session: ClientSession | None = None,
        headers: LooseHeaders | None = None,
        timeout: int | None = None,
        client_name: str | None = None,
        trace_configs: List[TraceConfig] | None = None,
    ):
        """
        Initialize Metis client.

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
        headers = headers or {}
        if session is None:
            session = aiohttp.ClientSession(
                timeout=timeout
                if isinstance(timeout, ClientTimeout)
                else ClientTimeout(total=timeout),
                headers=headers,
                trace_configs=trace_configs,
            )
            session.headers[USER_AGENT] = client_name or DEFAULT_USER_AGENT
            self._close_session = True
        self._session = session

        base_url = URL(base_url)
        client = MetisClient(session, base_url, auth)
        self._ns_root = MetisRootNamespace(client, base_url)

    @property
    def v0(self) -> MetisV0Namespace:
        """Property to access the v0 namespace."""
        return self._ns_root.v0

    @property
    def stream(self) -> MetisStreamNamespace:
        """Property to access the stream namespace."""
        return self._ns_root.stream

    async def __aenter__(self) -> "MetisAPI":
        """Async enter."""
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        self.stream.close()
        if self._session and self._close_session:
            return await self._session.close()
