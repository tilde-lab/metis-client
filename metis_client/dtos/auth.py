"""Authentication DTOs"""

import sys

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import TypedDict
else:  # pragma: no cover
    from typing import TypedDict


class MetisAuthCredentialsRequestDTO(TypedDict):
    "Authentication request payload"
    email: str
    password: str
