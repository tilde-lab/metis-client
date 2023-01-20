from dataclasses import dataclass
from typing import TypedDict, cast


class MetisMinimalDatasourcesResponse(TypedDict):
    name: str
    type: int
    id: int


@dataclass(frozen=True)
class MetisMinimalDatasourcesModel:
    id: int
    type: int
    name: str

    @classmethod
    def from_response(
        cls, data: MetisMinimalDatasourcesResponse
    ) -> "MetisMinimalDatasourcesModel":
        return cls(
            id=cast(int, data.get("id")),
            type=cast(int, data.get("type")),
            name=data.get("name", ""),
        )
