"""Constants for metis_client."""

from __future__ import annotations

from logging import Logger, getLogger
from typing import Literal, Union

PROJECT_VERSION = "0.0.3"
PROJECT_NAME = "metis_client"

# This is the default user agent,
# but it is adviced to use your own when building out your application
DEFAULT_USER_AGENT = f"metis_client/{PROJECT_VERSION}"


LOGGER: Logger = getLogger(PROJECT_NAME)

HttpMethods = Union[
    Literal["CONNECT"],
    Literal["HEAD"],
    Literal["GET"],
    Literal["DELETE"],
    Literal["OPTIONS"],
    Literal["PATCH"],
    Literal["POST"],
    Literal["PUT"],
    Literal["TRACE"],
]
