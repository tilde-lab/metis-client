"""Authenticators"""

from abc import abstractmethod
from asyncio import Lock, sleep

from aiohttp import ClientSession
from aiohttp.hdrs import METH_POST
from aiohttp.web_exceptions import HTTPTooManyRequests
from yarl import URL

from .models.auth import MetisAuthCredentialsModel
from .models.base import MetisBase


class BaseAuthenticator(MetisBase):
    """Base authentication class"""

    lock: Lock

    def __init__(self):
        self.lock = Lock()

    @abstractmethod
    async def authenticate(self, session: ClientSession, base_url: URL) -> bool:
        "Run authentication procedure"

    @abstractmethod
    async def should_update(self, session: ClientSession, base_url: URL) -> bool:
        "Check if authentication needed"


class MetisNoAuth(BaseAuthenticator):
    """No authentication (noop)"""

    async def authenticate(self, *_) -> bool:
        return True

    async def should_update(self, *_) -> bool:
        return False


class MetisTokenAuth(BaseAuthenticator):
    """Token based authentication"""

    _token: str

    def __init__(self, token: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._token = token

    async def authenticate(self, session: ClientSession, *_) -> bool:
        session.headers["Authorization"] = f"Bearer {self._token}"
        return True

    @classmethod
    def _get_cookie(cls, session: ClientSession, base_url: URL):
        return session.cookie_jar.filter_cookies(base_url).get("_sid")

    async def should_update(self, *_) -> bool:
        return True


class MetisLocalUserAuth(BaseAuthenticator):
    """Password based authentication"""

    _endpoint = "v0/auth"
    _credentials: MetisAuthCredentialsModel

    def __init__(self, email: str, password: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._credentials = MetisAuthCredentialsModel(email, password)
        self.logger.warning(
            "Please, don't use password based authentication - it's for testing only"
        )

    @classmethod
    def _get_cookie(cls, session: ClientSession, base_url: URL):
        return session.cookie_jar.filter_cookies(base_url).get("_sid")

    async def authenticate(self, session: ClientSession, base_url: URL) -> bool:
        async with session.request(
            METH_POST,
            base_url / self._endpoint,
            json=self._credentials.to_dto(),
            raise_for_status=False,
        ) as resp:
            if resp.status == HTTPTooManyRequests.status_code:
                await sleep(10)
                return await self.authenticate(session, base_url)
            return resp.ok and bool(self._get_cookie(session, base_url))

    async def should_update(self, session: ClientSession, base_url: URL) -> bool:
        session.cookie_jar.update_cookies({}, base_url)
        return not bool(self._get_cookie(session, base_url))
