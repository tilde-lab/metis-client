from typing import TypedDict
from dataclasses import dataclass


class MetisRequestIdResponce(TypedDict):
    reqId: str


@dataclass(frozen=True)
class MetisRequestIdModel:
    request_id: str

    @classmethod
    def from_response(cls, data: MetisRequestIdResponce) -> "MetisRequestIdModel":
        return cls(request_id=data.get("reqId"))
