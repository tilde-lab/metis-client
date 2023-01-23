from __future__ import annotations
from typing import TYPE_CHECKING

from yarl import URL

from ..models.base import MetisBase
from ..client import MetisClient

if TYPE_CHECKING:
    from .root import MetisRootNamespace

class BaseNamespace(MetisBase):
    """Used for the Metis API namespace."""

    _base_url: URL
    _client: MetisClient
    _auth_required: bool = True
    _root: "MetisRootNamespace"

    def __init__(
        self,
        client: MetisClient,
        base_url: URL,
        root: "MetisRootNamespace",
        auth_req: bool = True,
    ) -> None:
        """Initialise the namespace."""
        self._client = client
        self._base_url = base_url
        self._auth_required = auth_req
        self._root = root
        self.__post_init__()

    def __post_init__(self) -> None:
        """Post initialisation."""
