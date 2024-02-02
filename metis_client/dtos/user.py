"""User DTOs"""

import sys

from .base import MetisTimestampsDTO

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Dict
else:  # pragma: no cover
    Dict = dict

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import NotRequired
else:  # pragma: no cover
    from typing import NotRequired


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
