"""Data sources models"""

from dataclasses import dataclass
from typing import Sequence

from typing_extensions import TypedDict

from .collection import MetisCollectionDTO, MetisCollectionModel
from .timestamp import MetisTimestampsDTO, MetisTimestampsModel
from .user import MetisUserOnlyNameEmailDTO, MetisUserOnlyNameEmailModel


class MetisDataSourceDTO(MetisTimestampsDTO):
    "Data source DTO"

    id: int
    userId: int
    userFirstName: str
    userLastName: str
    userEmail: str
    name: str
    content: str
    type: int
    collections: Sequence[MetisCollectionDTO]
    progress: int


class MetisDataSourceContentOnlyDTO(TypedDict):
    "Data source content only DTO"
    content: str


@dataclass(frozen=True)
class MetisDataSourceModel(MetisTimestampsModel):
    "Data source model"

    id: int
    user: MetisUserOnlyNameEmailModel
    name: str
    content: str
    type: int
    collections: Sequence[MetisCollectionModel]
    progress: int

    @classmethod
    def from_dto(cls, dto: MetisDataSourceDTO) -> "MetisDataSourceModel":
        "Create model from DTO"
        user_dto: MetisUserOnlyNameEmailDTO = {
            "id": dto.get("userId"),
            "firstName": dto.get("firstName"),
            "lastName": dto.get("lastName"),
            "email": dto.get("userEmail"),
        }
        tsm = MetisTimestampsModel.from_dto(dto)
        return cls(
            id=dto.get("id"),
            user=MetisUserOnlyNameEmailModel.from_dto(user_dto),
            name=dto.get("name"),
            content=dto.get("content"),
            type=dto.get("type"),
            collections=[
                MetisCollectionModel.from_dto(x) for x in dto.get("collections") or []
            ],
            progress=dto.get("progress"),
            created_at=tsm.created_at,
            updated_at=tsm.updated_at,
        )


@dataclass(frozen=True)
class MetisDataSourceContentOnlyModel:
    "Data source content only model"

    content: str

    @classmethod
    def from_dto(
        cls, dto: MetisDataSourceContentOnlyDTO
    ) -> "MetisDataSourceContentOnlyModel":
        "Create model from DTO"
        return cls(content=dto.get("content"))
