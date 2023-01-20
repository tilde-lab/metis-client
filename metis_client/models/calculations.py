from dataclasses import dataclass
from typing import TypedDict, cast


class MetisMinimalCalculationsResponse(TypedDict):
    id: int
    name: str
    type: int


@dataclass(frozen=True)
class MetisMinimalCalculationsModel:
    id: int
    name: str
    type: int

    @classmethod
    def from_response(
        cls, data: MetisMinimalCalculationsResponse
    ) -> "MetisMinimalCalculationsModel":
        return cls(
            id=cast(int, data.get("id")),
            type=cast(int, data.get("type")),
            name=data.get("name", ""),
        )
