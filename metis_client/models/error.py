from dataclasses import dataclass
from typing import Dict, TypedDict


class MetisErrorResponse(TypedDict):
    status: int
    error: Dict | str | None


@dataclass(frozen=True)
class MetisErrorModel:
    status: int
    message: Dict | str | None

    @classmethod
    def from_response(cls, response: MetisErrorResponse) -> "MetisErrorModel":
        return cls(status=response.get("status"), message=response.get("error"))
