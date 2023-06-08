"""Root namespace"""

from yarl import URL

from ..client import MetisClient
from .base import BaseNamespace
from .calculations import MetisCalculationsNamespace
from .stream import MetisStreamNamespace
from .v0 import MetisV0Namespace


class MetisRootNamespace(BaseNamespace):
    """Root namespace"""

    def __init__(
        self,
        client: MetisClient,
        base_url: URL,
        root=None,
        auth_req: bool = True,
    ) -> None:
        """Initialise the namespace."""
        super().__init__(client, base_url, root or self, auth_req)

    def __post_init__(self) -> None:
        self.__ns_calculations = MetisCalculationsNamespace(
            self._client, self._base_url / "calculations", root=self
        )
        self.__ns_v0 = MetisV0Namespace(self._client, self._base_url / "v0", root=self)
        self.__ns_stream = MetisStreamNamespace(
            self._client, self._base_url / "stream", root=self
        )

    @property
    def calculations(self) -> "MetisCalculationsNamespace":
        """Property to access the calculations namespace."""
        return self.__ns_calculations

    @property
    def v0(self) -> "MetisV0Namespace":  # pylint: disable=invalid-name
        """Property to access the v0 namespace."""
        return self.__ns_v0

    @property
    def stream(self) -> "MetisStreamNamespace":
        """Property to access the stream namespace."""
        return self.__ns_stream
