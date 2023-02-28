"""Base of DTOs"""

import sys
from datetime import datetime

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import NotRequired, TypedDict
else:  # pragma: no cover
    from typing import NotRequired, TypedDict


class MetisTimestampsDTO(TypedDict):
    "Response with timestamps"
    createdAt: NotRequired[datetime]
    updatedAt: NotRequired[datetime]
