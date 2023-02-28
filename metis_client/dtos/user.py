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
    firstName: NotRequired[str]
    lastName: NotRequired[str]
    email: NotRequired[str]
    emailVerified: NotRequired[bool]
    roleLabel: NotRequired[str]
    roleSlug: NotRequired[str]
    permissions: NotRequired[Dict[str, str]]
    provider: NotRequired[str]
