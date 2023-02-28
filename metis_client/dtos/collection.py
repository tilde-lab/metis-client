"""Collections DTO's"""
import sys
from typing import Literal, Union

from .base import MetisTimestampsDTO

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Sequence
else:  # pragma: no cover
    from collections.abc import Sequence

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import NotRequired, TypedDict
else:  # pragma: no cover
    from typing import NotRequired, TypedDict


MetisCollectionVisibility = Union[
    Literal["private"], Literal["shared"], Literal["community"]
]


class MetisCollectionTypeDTO(MetisTimestampsDTO):
    "Collection type DTO"

    id: int
    slug: str
    label: str
    flavor: str


class MetisCollectionCommonDTO(TypedDict):
    "Common fields of collection's DTOs"

    title: str
    typeId: int
    dataSources: NotRequired[Sequence[int]]
    users: NotRequired[Sequence[int]]


class MetisCollectionCreateDTO(MetisCollectionCommonDTO):
    "Collection create DTO"

    description: NotRequired[str]


class MetisCollectionDTO(MetisCollectionCommonDTO, MetisTimestampsDTO):
    "Collection DTO"

    id: int
    description: str
    visibility: MetisCollectionVisibility

    userId: int
    userFirstName: NotRequired[str]
    userLastName: NotRequired[str]
    typeSlug: NotRequired[str]
    typeLabel: NotRequired[str]
    typeFlavor: NotRequired[str]
