"""Calculation models"""

from dataclasses import dataclass
from typing import Optional, Sequence

from .datasource import MetisDataSourceDTO, MetisDataSourceModel
from .timestamp import MetisTimestampsDTO, MetisTimestampsModel


class MetisCalculationDTO(MetisTimestampsDTO):
    "Calculation DTO"
    id: int
    name: str
    userId: int
    status: int
    progress: int
    result: Optional[Sequence[MetisDataSourceDTO]]


@dataclass(frozen=True)
class MetisCalculationModel(MetisTimestampsModel):
    "Calculation model"
    id: int
    name: str
    user_id: int
    status: int
    progress: int
    result: Sequence[MetisDataSourceModel]

    @classmethod
    def from_dto(cls, dto: MetisCalculationDTO) -> "MetisCalculationModel":
        "Create model from DTO"
        tsm = MetisTimestampsModel.from_dto(dto)
        return cls(
            id=dto.get("id"),
            name=dto.get("name"),
            user_id=dto.get("userId"),
            status=dto.get("status"),
            progress=dto.get("progress"),
            result=[MetisDataSourceModel.from_dto(x) for x in dto.get("result") or []],
            created_at=tsm.created_at,
            updated_at=tsm.updated_at,
        )
