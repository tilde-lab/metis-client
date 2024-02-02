"""Error DTOs"""

# pylint: disable=too-many-ancestors

import sys
from typing import Union

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import TypedDict
else:  # pragma: no cover
    from typing import TypedDict


class MetisErrorMessageDTO(TypedDict):
    "Error's raw transport error payload DTO"
    message: str


class MetisErrorDTO(TypedDict):
    "Error DTO"
    status: int
    error: Union[MetisErrorMessageDTO, str]
