"""Data sources DTOs"""

# pylint: disable=too-many-ancestors

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
    """The basic data types supported"""

    STRUCTURE = 1
    CALCULATION = 2
    PROPERTY = 3
    WORKFLOW = 4
    PATTERN = 5
    USER_INPUT = 6


class MetisDataSourceDTO(MetisTimestampsDTO):
    """A basic data item definition"""

    id: int
    parents: Sequence[int]
    children: Sequence[int]
    user_id: int
    user_first_name: str
    user_last_name: str
    user_email: str
    name: str
    content: str
    type: int
    collections: Sequence[MetisCollectionDTO]


class MetisDataSourceContentOnlyDTO(TypedDict):
    """Helper definition"""

    content: str
