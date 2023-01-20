from datetime import datetime
import json
from dataclasses import dataclass
from typing import Dict, List, Sequence, TypeVar, cast

from aiohttp_sse_client.client import MessageEvent
from metis_client.models.calculations import (
    MetisMinimalCalculationsModel,
    MetisMinimalCalculationsResponse,
)

from metis_client.models.datasources import (
    MetisMinimalDatasourcesModel,
    MetisMinimalDatasourcesResponse,
)

from .error import MetisErrorResponse, MetisErrorModel
from .user import MetisPrefixedMinimalUserResponse, MetisMinimalUserModel
from .collection import MetisCollectionTypeResponse, MetisCollectionTypeModel
from ..helpers import parse_rfc3339


@dataclass(frozen=True)
class MetisErrorEvent:
    request_id: str
    errors: Sequence[MetisErrorModel]

    @classmethod
    def from_message_event(cls, evt: MessageEvent) -> "MetisErrorEvent":
        if evt.type != "errors" or evt.message != "errors":
            raise TypeError("Unknown event type")

        payload = json.loads(evt.data)
        errors = []
        for err_dict in payload.get("data", []):
            err_dict = cast(MetisErrorResponse, err_dict)
            errors.append(MetisErrorModel.from_response(err_dict))

        return cls(request_id=payload.get("reqId"), errors=errors)


@dataclass(frozen=True)
class MetisPongEvent:
    @classmethod
    def from_message_event(cls, evt: MessageEvent) -> "MetisPongEvent":
        if not evt.type is None or evt.message != "" or evt.data != "pong":
            raise TypeError("Event type mismatch")
        return cls()


class MetisDatasourcesDataResponse(
    MetisMinimalDatasourcesResponse, MetisPrefixedMinimalUserResponse
):
    createdAt: str
    updatedAt: str


@dataclass(frozen=True)
class MetisDatasourcesModel(MetisMinimalDatasourcesModel):
    user: MetisMinimalUserModel
    type: MetisCollectionTypeModel | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class MetisDatasourcesEvent:
    request_id: str
    total: int
    types: Sequence[MetisCollectionTypeModel]
    data: Sequence[MetisDatasourcesModel]

    @classmethod
    def from_message_event(cls, evt: MessageEvent) -> "MetisDatasourcesEvent":
        if evt.type != "datasources" or evt.message != "datasources":
            raise TypeError("Event type mismatch")
        payload = json.loads(evt.data)

        types: Dict[int, MetisCollectionTypeModel] = {}
        for type_dict in payload.get("types", []):
            type_dict = cast(MetisCollectionTypeResponse, type_dict)
            t = MetisCollectionTypeModel.from_response(type_dict)
            types[t.id] = t

        data: List[MetisDatasourcesModel] = []
        for data_dict in payload.get("data", []):
            data_dict = cast(MetisDatasourcesDataResponse, data_dict)
            d = MetisMinimalDatasourcesModel.from_response(data_dict)
            data.append(
                MetisDatasourcesModel(
                    id=d.id,
                    name=d.name,
                    created_at=parse_rfc3339(data_dict.get("createdAt"))
                    or datetime.fromtimestamp(0),
                    updated_at=parse_rfc3339(data_dict.get("updatedAt"))
                    or datetime.fromtimestamp(0),
                    user=MetisMinimalUserModel.from_prefixed_response(data_dict),
                    type=types.get(d.type),
                )
            )

        return cls(
            request_id=payload.get("reqId"),
            total=payload.get("total", 0),
            types=list(types.values()),
            data=data,
        )


data = {
    "type": 2,
    "name": "Au",
    "progress": 25,
    "id": 2,
    "userId": 1,
    "createdAt": "2023-01-20T17:59:34.176Z",
    "updatedAt": "2023-01-20T17:59:34.176Z",
}


class MetisCalculationsDataResponse(MetisMinimalCalculationsResponse):
    userId: int
    createdAt: str
    updatedAt: str


@dataclass(frozen=True)
class MetisCalculationsModel:
    id: int
    name: str
    progress: int
    user_id: int
    type: MetisCollectionTypeModel | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class MetisCalculationsEvent:
    request_id: int
    total: int
    types: Sequence[MetisCollectionTypeModel]
    data: Sequence[MetisCalculationsModel]

    @classmethod
    def from_message_event(cls, evt: MessageEvent) -> "MetisCalculationsEvent":
        if evt.type != "calculations" or evt.message != "calculations":
            raise TypeError("Event type mismatch")
        payload = json.loads(evt.data)

        types: Dict[int, MetisCollectionTypeModel] = {}
        for type_dict in payload.get("types", []):
            type_dict = cast(MetisCollectionTypeResponse, type_dict)
            t = MetisCollectionTypeModel.from_response(type_dict)
            types[t.id] = t

        data: List[MetisCalculationsModel] = []
        for data_dict in payload.get("data", []):
            data_dict = cast(MetisCalculationsDataResponse, data_dict)
            c = MetisMinimalCalculationsModel.from_response(data_dict)
            data.append(
                MetisCalculationsModel(
                    id=c.id,
                    name=c.name,
                    progress=data_dict.get("progress", 0),
                    created_at=parse_rfc3339(data_dict.get("createdAt"))
                    or datetime.fromtimestamp(0),
                    updated_at=parse_rfc3339(data_dict.get("updatedAt"))
                    or datetime.fromtimestamp(0),
                    user_id=cast(int, types.get(c.type)),
                    type=types.get(c.type),
                )
            )

        return cls(
            request_id=payload.get("reqId"),
            total=payload.get("total", 0),
            types=list(types.values()),
            data=data,
        )


@dataclass(frozen=True)
class MetisOtherEvent:
    type: str
    message: str
    data: str

    @classmethod
    def from_message_event(cls, evt: MessageEvent) -> "MetisOtherEvent":
        return cls(type=evt.type, message=evt.message, data=evt.data)


MetisEvents = (
    MetisErrorEvent
    | MetisPongEvent
    | MetisDatasourcesEvent
    | MetisCalculationsEvent
    | MetisOtherEvent
)
MetisEventType = TypeVar("MetisEventType", bound=MetisErrorEvent)
