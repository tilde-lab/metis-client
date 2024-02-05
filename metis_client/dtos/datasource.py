"""Data sources DTOs"""

# pylint: disable=too-many-ancestors

from enum import Enum

from ..compat import Sequence, TypedDict
from .base import MetisTimestampsDTO
from .collection import MetisCollectionDTO


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
