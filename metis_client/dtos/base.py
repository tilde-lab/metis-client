"""Base of DTOs"""

from datetime import datetime

from ..compat import NotRequired, TypedDict


class MetisTimestampsDTO(TypedDict):
    "Response with timestamps"
    created_at: NotRequired[datetime]
    updated_at: NotRequired[datetime]
