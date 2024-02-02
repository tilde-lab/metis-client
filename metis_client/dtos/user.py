"""User DTOs"""

from ..compat import Dict, NotRequired
from .base import MetisTimestampsDTO


class MetisUserDTO(MetisTimestampsDTO):
    "User DTO"

    id: int
    first_name: NotRequired[str]
    last_name: NotRequired[str]
    email: NotRequired[str]
    email_verified: NotRequired[bool]
    role_label: NotRequired[str]
    role_slug: NotRequired[str]
    permissions: NotRequired[Dict[str, str]]
    provider: NotRequired[str]
