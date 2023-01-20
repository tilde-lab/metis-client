from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict, cast

from ..helpers import parse_rfc3339


class MetisMininalCollectionTypeResponse(TypedDict):
    id: int
    slug: str | None
    label: str | None
    flavor: str | None


class MetisCollectionTypeResponse(MetisMininalCollectionTypeResponse):
    createdAt: str
    updatedAt: str


@dataclass(frozen=True)
class MetisCollectionTypeModel:
    id: int
    slug: str | None
    label: str | None
    flavor: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_response(
        cls, data: MetisCollectionTypeResponse
    ) -> "MetisCollectionTypeModel":
        return cls(
            id=cast(int, data.get("id")),
            slug=data.get("slug"),
            label=data.get("label"),
            flavor=data.get("flavor"),
            created_at=parse_rfc3339(data.get("createdAt"))
            or datetime.fromtimestamp(0),
            updated_at=parse_rfc3339(data.get("updatedAt"))
            or datetime.fromtimestamp(0),
        )
