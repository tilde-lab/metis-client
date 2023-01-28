"""User models"""

from dataclasses import dataclass
from typing import Dict, Optional, TypedDict

from .timestamp import MetisTimestampsDTO


class MetisUserOnlyNameEmailDTO(TypedDict):
    "User DTO but only id, name, email"
    id: int
    firstName: Optional[str]
    lastName: Optional[str]
    email: Optional[str]


@dataclass(frozen=True)
class MetisUserOnlyNameEmailModel:
    "User model but only id, name, email"

    id: int
    email: str
    first_name: str
    last_name: str

    @classmethod
    def from_dto(cls, dto: MetisUserOnlyNameEmailDTO) -> "MetisUserOnlyNameEmailModel":
        "Create model from DTO"
        return cls(
            id=dto.get("id"),
            email=dto.get("email") or "",
            first_name=dto.get("firstName") or "",
            last_name=dto.get("lastName") or "",
        )


class MetisUserDTO(MetisUserOnlyNameEmailDTO, MetisTimestampsDTO):
    "User DTO"

    emailVerified: Optional[bool]
    roleLabel: Optional[str]
    roleSlug: Optional[str]
    permissions: Optional[Dict[str, str]]
    provider: Optional[str]


@dataclass(frozen=True)
class MetisUserModel:
    "User model"

    id: int
    email: str
    first_name: str
    last_name: str
    email_verified: Optional[bool]
    role_label: Optional[str]
    role_slug: Optional[str]
    permissions: Optional[Dict[str, str]]
    provider: Optional[str]

    @classmethod
    def from_dto(cls, dto: MetisUserDTO) -> "MetisUserModel":
        "Create model from DTO"
        min_user = MetisUserOnlyNameEmailModel.from_dto(dto)
        return cls(
            id=min_user.id,
            email=min_user.email,
            first_name=min_user.first_name,
            last_name=min_user.last_name,
            email_verified=dto.get("emailVerified"),
            role_label=dto.get("roleLabel"),
            role_slug=dto.get("roleSlug"),
            permissions=dto.get("permissions"),
            provider=dto.get("provider"),
        )
