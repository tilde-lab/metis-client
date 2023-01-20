from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, cast, TypedDict

from .user import MetisMinimalUserResponse, MetisMinimalUserModel
from ..helpers import parse_rfc3339


class MetisAuthCredentialsRequestPayload(TypedDict):
    email: str
    password: str


@dataclass(frozen=True)
class MetisAuthCredentialsModel:
    email: str
    password: str

    def to_request(self) -> MetisAuthCredentialsRequestPayload:
        return MetisAuthCredentialsRequestPayload(**asdict(self))


class MetisWhoAmIProviderResponse(TypedDict):
    provider: str
    providerId: int
    profile: Dict
    createdAt: str
    updatedAt: str


@dataclass(frozen=True)
class MetisWhoAmIProviderModel:
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    profile: Dict

    @classmethod
    def from_response(
        cls, data: MetisWhoAmIProviderResponse
    ) -> "MetisWhoAmIProviderModel":
        return cls(
            id=cast(int, data.get("providerId")),
            name=data.get("provider"),
            profile=data.get("profile", {}),
            created_at=parse_rfc3339(data.get("createdAt"))
            or datetime.fromtimestamp(0),
            updated_at=parse_rfc3339(data.get("updatedAt"))
            or datetime.fromtimestamp(0),
        )


class MetisWhoAmIResponse(MetisMinimalUserResponse):
    createdAt: str
    updatedAt: str
    roleLabel: str | None
    roleSlug: str | None
    permissions: Dict[str, str]
    emailVerified: bool | None
    provider: MetisWhoAmIProviderResponse | None


@dataclass(frozen=True)
class MetisWhoAmIModel(MetisMinimalUserModel):
    created_at: datetime
    updated_at: datetime
    role_label: str | None
    role_slug: str | None
    permissions: Dict[str, str]
    email_verified: bool | None
    provider: MetisWhoAmIProviderModel | None

    @classmethod
    def from_response(cls, data: MetisWhoAmIResponse) -> "MetisWhoAmIModel":
        provider_dict = data.get("provider")
        min_user = MetisMinimalUserModel.from_response(data)
        return cls(
            id=min_user.id,
            created_at=parse_rfc3339(data.get("createdAt"))
            or datetime.fromtimestamp(0),
            updated_at=parse_rfc3339(data.get("updatedAt"))
            or datetime.fromtimestamp(0),
            first_name=min_user.first_name,
            last_name=min_user.last_name,
            role_label=data.get("roleLabel"),
            role_slug=data.get("roleSlug"),
            permissions=data.get("permissions", {}),
            email=min_user.email,
            email_verified=data.get("emailVerified"),
            provider=MetisWhoAmIProviderModel.from_response(provider_dict)
            if provider_dict
            else None,
        )
