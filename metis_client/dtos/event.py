"""Event DTOs"""
import sys
from typing import Literal, Union

from .calculation import MetisCalculationDTO
from .collection import MetisCollectionDTO, MetisCollectionTypeDTO
from .datasource import MetisDataSourceDTO
from .error import MetisErrorDTO

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Sequence
else:  # pragma: no cover
    from collections.abc import Sequence

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import TypedDict
else:  # pragma: no cover
    from typing import TypedDict

MetisEventType = Literal["calculations", "collections", "datasources", "errors", "pong"]


class MetisErrorEventDataDTO(TypedDict):
    "Errors event data DTO"
    reqId: str
    data: Sequence[MetisErrorDTO]


class MetisErrorEventDTO(TypedDict):
    "Errors event DTO"
    type: Literal["errors"]
    data: MetisErrorEventDataDTO


class MetisPongEventDTO(TypedDict):
    "Pong event DTO"
    type: Literal["pong"]
    data: None


class MetisDataSourcesEventDataDTO(TypedDict):
    "Data sources event data DTO"
    reqId: str
    data: Sequence[MetisDataSourceDTO]
    total: int
    types: Sequence[MetisCollectionTypeDTO]


class MetisDataSourcesEventDTO(TypedDict):
    "Data sources event DTO"
    type: Literal["datasources"]
    data: MetisDataSourcesEventDataDTO


class MetisCalculationsEventDataDTO(TypedDict):
    "Calculations event data DTO"
    reqId: str
    data: Sequence[MetisCalculationDTO]
    total: int
    types: Sequence[MetisCollectionTypeDTO]


class MetisCalculationsEventDTO(TypedDict):
    "Calculations event DTO"
    type: Literal["calculations"]
    data: MetisCalculationsEventDataDTO


class MetisCollectionsEventDataDTO(TypedDict):
    "Collections event data DTO"
    reqId: str
    data: Sequence[MetisCollectionDTO]
    total: int
    types: Sequence[MetisCollectionTypeDTO]


class MetisCollectionsEventDTO(TypedDict):
    "Collections event DTO"
    type: Literal["collections"]
    data: MetisCollectionsEventDataDTO


MetisEventDTO = Union[
    MetisCalculationsEventDTO,
    MetisCollectionsEventDTO,
    MetisDataSourcesEventDTO,
    MetisErrorEventDTO,
    MetisPongEventDTO,
]
