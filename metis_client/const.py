"""Constants for metis_client."""

from __future__ import annotations
from enum import Enum
from logging import Logger, getLogger
from typing import Literal, TypeVar, Union

GenericType = TypeVar("GenericType")

PROJECT_VERSION = "0.0.1"
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


class HttpContentType(str, Enum):
    """HTTP Content Types."""

    BASE_JSON = "application/json"

    JSON = "application/json;charset=utf-8"
    TEXT_PLAIN = "text/plain;charset=utf-8"
    TEXT_HTML = "text/html;charset=utf-8"
    TEXT_EVENT_STREAM = "text/event-stream"

    UNKNOWN = "UNKNOWN"
