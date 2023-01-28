"""Error models"""

from dataclasses import dataclass
from typing import TypedDict, Union


class MetisErrorErrorDTO(TypedDict):
    "Error's error payload DTO"
    message: str


class MetisErrorDTO(TypedDict):
    "Error DTO"
    status: int
    error: Union[MetisErrorErrorDTO, str]


@dataclass(frozen=True)
class MetisErrorErrorModel:
    "Error's error model"
    message: str

    @classmethod
    def from_dto(
        cls, data: Union[MetisErrorErrorDTO, str]
    ) -> Union["MetisErrorErrorModel", str]:
        "Create model from DTO"
        if isinstance(data, dict):
            return cls(message=data.get("message", ""))
        return data


@dataclass(frozen=True)
class MetisErrorModel:
    "Error model"
    status: int
    message: Union[MetisErrorErrorModel, str]

    @classmethod
    def from_dto(cls, response: MetisErrorDTO) -> "MetisErrorModel":
        "Create model from DTO"
        return cls(
            status=response.get("status"),
            message=MetisErrorErrorModel.from_dto(response.get("error", "")),
        )
