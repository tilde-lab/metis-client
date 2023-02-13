"""Event models"""

import json
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, Any, Literal, Optional, Sequence, Union

from aiohttp_sse_client.client import MessageEvent
from typing_extensions import TypedDict

from .calculation import MetisCalculationDTO, MetisCalculationModel
from .collection import (
    MetisCollectionDTO,
    MetisCollectionModel,
    MetisCollectionTypeDTO,
    MetisCollectionTypeModel,
)
from .datasource import MetisDataSourceDTO, MetisDataSourceModel
from .error import MetisErrorDTO, MetisErrorModel

if TYPE_CHECKING:
    from typing_extensions import Self, TypeGuard

EventType = Union[
    Literal["calculations"],
    Literal["collections"],
    Literal["datasources"],
    Literal["errors"],
    Literal["pong"],
]


class MetisEventGuard:
    "Base event class with guard"

    @classmethod
    def guard(cls, obj: Any) -> "TypeGuard[Self]":
        "Type guard for self"
        return isinstance(obj, cls)


class MetisErrorEventDataDTO(TypedDict):
    "Errors event data DTO"
    reqId: str
    data: Sequence[MetisErrorDTO]


class MetisErrorEventDTO(TypedDict):
    "Errors event DTO"
    type: Literal["errors"]
    data: MetisErrorEventDataDTO


@dataclass(frozen=True)
class MetisErrorEventModel(MetisEventGuard):
    "Error event model"
    request_id: str
    errors: Sequence[MetisErrorModel]

    @classmethod
    def from_dto(cls, dto: MetisErrorEventDTO) -> "MetisErrorEventModel":
        "Create model from DTO"
        return cls(
            dto.get("data", {}).get("reqId", ""),
            [MetisErrorModel.from_dto(x) for x in dto.get("data", {}).get("data", [])],
        )


class MetisPongEventDTO(TypedDict):
    "Pong event DTO"
    type: Literal["pong"]
    data: None


@dataclass(frozen=True)
class MetisPongEventModel(MetisEventGuard):
    "Pong event model"

    request_id: Optional[str] = None

    @classmethod
    def from_dto(cls, _: MetisPongEventDTO) -> "MetisPongEventModel":
        "Create model from DTO"
        return cls()


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


@dataclass(frozen=True)
class MetisDataSourcesEventModel(MetisEventGuard):
    "Data sources event model"
    request_id: str
    total: int
    types: Sequence[MetisCollectionTypeModel]
    data: Sequence[MetisDataSourceModel]

    @classmethod
    def from_dto(cls, dto: MetisDataSourcesEventDTO) -> "MetisDataSourcesEventModel":
        "Create model from DTO"
        return cls(
            dto.get("data", {}).get("reqId", ""),
            dto.get("data", {}).get("total", 0),
            [
                MetisCollectionTypeModel.from_dto(x)
                for x in dto.get("data", {}).get("types", [])
            ],
            [
                MetisDataSourceModel.from_dto(x)
                for x in dto.get("data", {}).get("data", [])
            ],
        )


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


@dataclass(frozen=True)
class MetisCalculationsEventModel(MetisEventGuard):
    "Calculations event model"
    request_id: str
    total: int
    types: Sequence[MetisCollectionTypeModel]
    data: Sequence[MetisCalculationModel]

    @classmethod
    def from_dto(cls, dto: MetisCalculationsEventDTO) -> "MetisCalculationsEventModel":
        "Create model from DTO"
        return cls(
            dto.get("data", {}).get("reqId", ""),
            dto.get("data", {}).get("total", 0),
            [
                MetisCollectionTypeModel.from_dto(x)
                for x in dto.get("data", {}).get("types", [])
            ],
            [
                MetisCalculationModel.from_dto(x)
                for x in dto.get("data", {}).get("data", [])
            ],
        )


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


@dataclass(frozen=True)
class MetisCollectionsEventModel(MetisEventGuard):
    "Collections event model"
    request_id: str
    total: int
    types: Sequence[MetisCollectionTypeModel]
    data: Sequence[MetisCollectionModel]

    @classmethod
    def from_dto(cls, dto: MetisCollectionsEventDTO) -> "MetisCollectionsEventModel":
        "Create model from DTO"
        return cls(
            dto.get("data", {}).get("reqId", ""),
            dto.get("data", {}).get("total", 0),
            [
                MetisCollectionTypeModel.from_dto(x)
                for x in dto.get("data", {}).get("types", [])
            ],
            [
                MetisCollectionModel.from_dto(x)
                for x in dto.get("data", {}).get("data", [])
            ],
        )


MetisEventDTO = Union[
    MetisCalculationsEventDTO,
    MetisCollectionsEventDTO,
    MetisDataSourcesEventDTO,
    MetisErrorEventDTO,
    MetisPongEventDTO,
]


@dataclass(frozen=True)
class MetisMessageEvent(MessageEvent):
    "SSE Message Event"

    type: str
    message: str
    data: str
    origin: str
    last_event_id: str

    @classmethod
    def from_dto(cls, data: MessageEvent) -> "MetisMessageEvent":
        "Create model from DTO"
        return cls(
            type=data.type,
            message=data.message,
            data=data.data,
            origin=data.origin,
            last_event_id=data.last_event_id,
        )

    def to_dto(self) -> MetisEventDTO:
        "Create DTO from model"
        try:
            if self.type is None and self.message == "" and self.data == "pong":
                return MetisPongEventDTO(type="pong", data=None)
            for dto in (
                partial(MetisErrorEventDTO, type="errors"),
                partial(MetisDataSourcesEventDTO, type="datasources"),
                partial(MetisCalculationsEventDTO, type="calculations"),
                partial(MetisCollectionsEventDTO, type="collections"),
            ):
                if dto.keywords["type"] in [self.type, self.message]:
                    return dto(data=json.loads(self.data))
        except json.JSONDecodeError as err:
            return MetisErrorEventDTO(
                type="errors",
                data=MetisErrorEventDataDTO(
                    reqId="",
                    data=[MetisErrorDTO(status=400, error=str(err))],
                ),
            )
        message = f"Unknown event type: {str(self)}"
        return MetisErrorEventDTO(
            type="errors",
            data=MetisErrorEventDataDTO(
                reqId="",
                data=[MetisErrorDTO(status=400, error=message)],
            ),
        )


MetisDataEvent = Union[
    MetisCalculationsEventModel, MetisCollectionsEventModel, MetisDataSourcesEventModel
]
MetisEvent = Union[MetisDataEvent, MetisErrorEventModel, MetisPongEventModel]


def cast_event(dto: MetisEventDTO) -> MetisEvent:
    "Try to convert message to the typed event"
    if dto["type"] == "pong":
        return MetisPongEventModel.from_dto(dto)
    if dto["type"] == "datasources":
        return MetisDataSourcesEventModel.from_dto(dto)
    if dto["type"] == "calculations":
        return MetisCalculationsEventModel.from_dto(dto)
    if dto["type"] == "collections":
        return MetisCollectionsEventModel.from_dto(dto)
    if dto["type"] == "errors":
        return MetisErrorEventModel.from_dto(dto)
    # never
    return MetisErrorEventModel.from_dto(dto)
