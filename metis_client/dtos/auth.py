"""Authentication DTOs"""

from ..compat import TypedDict


class MetisAuthCredentialsRequestDTO(TypedDict):
    "Authentication request payload"
    email: str
    password: str
