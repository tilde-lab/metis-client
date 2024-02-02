"""Error DTOs"""

# pylint: disable=too-many-ancestors

from typing import Union

from ..compat import TypedDict


class MetisErrorMessageDTO(TypedDict):
    "Error's raw transport error payload DTO"
    message: str


class MetisErrorDTO(TypedDict):
    "Error DTO"
    status: int
    error: Union[MetisErrorMessageDTO, str]
