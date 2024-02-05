"""SSE models"""

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
from ..helpers import metis_json_decoder


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
                    data = metis_json_decoder(self.data)

                    return dto(data=data)
        except json.JSONDecodeError as err:
            return MetisErrorEventDTO(
                type="errors",
                data={
                    "req_id": "",
                    "data": [MetisErrorDTO(status=400, error=str(err))],
                },
            )
        message = f"Unknown event type: {str(self)}"
        return MetisErrorEventDTO(
            type="errors",
            data={"req_id": "", "data": [MetisErrorDTO(status=400, error=message)]},
        )
