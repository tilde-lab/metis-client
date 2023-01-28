"""Collections models"""

from dataclasses import dataclass
from typing import Literal, Optional, Sequence, Union

from .timestamp import MetisTimestampsDTO, MetisTimestampsModel
from .user import MetisUserOnlyNameEmailDTO, MetisUserOnlyNameEmailModel

MetisCollectionVisibility = Union[
    Literal["private"], Literal["shared"], Literal["community"]
]


class MetisCollectionTypeDTO(MetisTimestampsDTO):
    "Collection type DTO"

    id: int
    slug: str
    label: str
    flavor: str


@dataclass(frozen=True)
class MetisCollectionTypeModel(MetisTimestampsModel):
    "Collection type model"

    id: int
    slug: str
    label: str
    flavor: str

    @classmethod
    def from_dto(cls, dto: MetisCollectionTypeDTO) -> "MetisCollectionTypeModel":
        "Create model from DTO"
        tsm = MetisTimestampsModel.from_dto(dto)
        return cls(
            id=dto["id"],
            slug=dto.get("slug"),
            label=dto.get("label"),
            flavor=dto.get("flavor"),
            created_at=tsm.created_at,
            updated_at=tsm.updated_at,
        )


class MetisCollectionDTO(MetisTimestampsDTO):
    "Collection DTO"

    id: int
    title: str
    description: str
    visibility: MetisCollectionVisibility

    userId: int
    userFirstName: Optional[str]
    userLastName: Optional[str]
    typeId: int
    typeSlug: Optional[str]
    typeLabel: Optional[str]
    typeFlavor: Optional[str]

    dataSources: Optional[Sequence[int]]
    users: Optional[Sequence[int]]


@dataclass(frozen=True)
class MetisCollectionModel(MetisTimestampsModel):
    "Collection model"

    id: int
    title: str
    description: str
    visibility: MetisCollectionVisibility
    user: MetisUserOnlyNameEmailModel
    type: MetisCollectionTypeModel
    data_sources: Sequence[int]
    users: Sequence[int]

    @classmethod
    def from_dto(cls, dto: MetisCollectionDTO) -> "MetisCollectionModel":
        "Create model from DTO"
        user_dto: MetisUserOnlyNameEmailDTO = {
            "id": dto.get("userId"),
            "firstName": dto.get("firstName"),
            "lastName": dto.get("lastName"),
            "email": dto.get("userEmail"),
        }
        type_dto: MetisCollectionTypeDTO = {
            "id": dto.get("typeId"),
            "slug": dto.get("typeSlug") or "",
            "label": dto.get("typeLabel") or "",
            "flavor": dto.get("typeFlavor") or "",
            "createdAt": None,
            "updatedAt": None,
        }
        tsm = MetisTimestampsModel.from_dto(dto)
        return cls(
            id=dto.get("id"),
            title=dto.get("title"),
            description=dto.get("description"),
            visibility=dto.get("visibility"),
            user=MetisUserOnlyNameEmailModel.from_dto(user_dto),
            type=MetisCollectionTypeModel.from_dto(type_dto),
            data_sources=dto.get("dataSources") or [],
            users=dto.get("users") or [],
            created_at=tsm.created_at,
            updated_at=tsm.updated_at,
        )
