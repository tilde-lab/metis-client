"""Data sources DTOs"""

import sys
from enum import Enum

from .base import MetisTimestampsDTO
from .collection import MetisCollectionDTO

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Sequence
else:  # pragma: no cover
    from collections.abc import Sequence

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import TypedDict
else:  # pragma: no cover
    from typing import TypedDict


class DataSourceType(int, Enum):
    "Data source types"
    STRUCTURE = 1
    CALCULATION = 2
    PROPERTY = 3
    WORKFLOW = 4
    PATTERN = 5


class MetisDataSourceDTO(MetisTimestampsDTO):
    "Data source DTO"

    id: int
    parents: Sequence[int]
    children: Sequence[int]
    userId: int
    userFirstName: str
    userLastName: str
    userEmail: str
    name: str
    content: str
    type: int
    collections: Sequence[MetisCollectionDTO]


class MetisDataSourceContentOnlyDTO(TypedDict):
    "Data source content only DTO"
    content: str
