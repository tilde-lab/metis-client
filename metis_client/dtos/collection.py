"""Collections DTOs"""

# pylint: disable=too-many-ancestors

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
    "Common fields of collection DTOs"

    id: NotRequired[int]
    title: str
    type_id: int
    data_sources: NotRequired[Sequence[int]]
    users: NotRequired[Sequence[int]]


class MetisCollectionCreateDTO(MetisCollectionCommonDTO):
    "Collection create DTO"

    description: NotRequired[str]
    visibility: NotRequired[MetisCollectionVisibility]


class MetisCollectionDTO(MetisCollectionCommonDTO, MetisTimestampsDTO):
    "Collection DTO"

    id: int
    description: str
    visibility: MetisCollectionVisibility

    user_id: int
    user_first_name: NotRequired[str]
    user_last_name: NotRequired[str]
    type_slug: NotRequired[str]
    type_label: NotRequired[str]
    type_flavor: NotRequired[str]
