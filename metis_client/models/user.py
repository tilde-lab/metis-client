from dataclasses import dataclass
from typing import Dict, TypedDict, cast


class MetisMinimalUserResponse(TypedDict):
    id: int
    email: str
    firstName: str
    lastName: str


class MetisPrefixedMinimalUserResponse(TypedDict):
    userId: int
    userEmail: str
    userFirstName: str
    userLastName: str


@dataclass(frozen=True)
class MetisMinimalUserModel:
    id: int
    email: str
    first_name: str
    last_name: str

    @classmethod
    def from_response(cls, data: MetisMinimalUserResponse) -> "MetisMinimalUserModel":
        return cls(
            id=cast(int, data.get("id")),
            first_name=data.get("firstName", ""),
            last_name=data.get("lastName", ""),
            email=data.get("email", ""),
        )

    @classmethod
    def from_prefixed_response(cls, data: MetisPrefixedMinimalUserResponse) -> "MetisMinimalUserModel":
        return cls(
            id=cast(int, data.get("userId")),
            first_name=data.get("userFirstName", ""),
            last_name=data.get("userLastName", ""),
            email=data.get("userEmail", ""),
        )
