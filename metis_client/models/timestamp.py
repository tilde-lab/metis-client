"""Timestamps model and DTO"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TypedDict

from ..helpers import parse_rfc3339


class MetisTimestampsDTO(TypedDict):
    "Response with timestamps"
    createdAt: Optional[str]
    updatedAt: Optional[str]


@dataclass(frozen=True)
class MetisTimestampsModel:
    "Timestamps model"

    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto: MetisTimestampsDTO) -> "MetisTimestampsModel":
        "Create model from DTO"
        return cls(
            created_at=parse_rfc3339(dto.get("createdAt")) or datetime.fromtimestamp(0),
            updated_at=parse_rfc3339(dto.get("updatedAt")) or datetime.fromtimestamp(0),
        )
