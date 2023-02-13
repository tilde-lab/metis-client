"Base response model"

from dataclasses import dataclass

from typing_extensions import TypedDict


class MetisRequestIdDTO(TypedDict):
    "Response with request id dictionary"
    reqId: str


@dataclass(frozen=True)
class MetisRequestIdModel:
    "Response with request id model"
    request_id: str

    @classmethod
    def from_dto(cls, data: MetisRequestIdDTO) -> "MetisRequestIdModel":
        "Create model from response"
        return cls(request_id=data["reqId"])
