"""Event models"""

import json
from dataclasses import dataclass
from functools import partial

from aiohttp_sse_client.client import MessageEvent

from ..dtos import (
    MetisCalculationsEventDTO,
    MetisCollectionsEventDTO,
    MetisDataSourcesEventDTO,
    MetisErrorDTO,
    MetisErrorEventDTO,
    MetisEventDTO,
    MetisPongEventDTO,
)
from ..helpers import dict_dt_from_dt_str


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
                    data = json.loads(self.data)
                    # convert date strings to datetime
                    if isinstance(data, dict) and isinstance(data.get("data"), list):
                        data["data"] = list(map(dict_dt_from_dt_str, data["data"]))
                    if isinstance(data, dict) and isinstance(data.get("types"), list):
                        data["types"] = list(map(dict_dt_from_dt_str, data["types"]))

                    return dto(data=data)
        except json.JSONDecodeError as err:
            return MetisErrorEventDTO(
                type="errors",
                data={"reqId": "", "data": [MetisErrorDTO(status=400, error=str(err))]},
            )
        message = f"Unknown event type: {str(self)}"
        return MetisErrorEventDTO(
            type="errors",
            data={"reqId": "", "data": [MetisErrorDTO(status=400, error=message)]},
        )
