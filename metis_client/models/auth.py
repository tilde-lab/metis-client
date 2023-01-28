"""Authentication models"""

from dataclasses import asdict, dataclass
from typing import TypedDict


class MetisAuthCredentialsRequestDTO(TypedDict):
    "Authentication request payload"
    email: str
    password: str


@dataclass(frozen=True)
class MetisAuthCredentialsModel:
    "Authentication payload model"
    email: str
    password: str

    def to_dto(self) -> MetisAuthCredentialsRequestDTO:
        "Render model to request payload"
        return MetisAuthCredentialsRequestDTO(**asdict(self))
