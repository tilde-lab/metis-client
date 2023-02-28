"""Small helpers"""

import re
import sys
from contextlib import suppress
from copy import deepcopy
from datetime import datetime
from functools import partial, wraps
from typing import Any, Optional, Type, TypeVar, cast

from aiohttp.web_exceptions import (
    HTTPBadRequest,
    HTTPForbidden,
    HTTPMisdirectedRequest,
    HTTPNotFound,
    HTTPPaymentRequired,
    HTTPUnauthorized,
)

from .dtos import MetisErrorDTO, MetisErrorEventDTO, MetisEventDTO
from .exc import (
    MetisAuthenticationException,
    MetisError,
    MetisNotFoundException,
    MetisPayloadException,
    MetisQuotaException,
)

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Mapping, Sequence, Tuple
else:  # pragma: no cover
    from collections.abc import Mapping, Sequence

    Tuple = tuple

if sys.version_info < (3, 10):  # pragma: no cover
    from typing_extensions import TypeGuard
else:  # pragma: no cover
    from typing import TypeGuard


LAST_Z_REGEX = re.compile(r"Z$", re.IGNORECASE)


def parse_rfc3339(dt_str: Any) -> Optional[datetime]:
    "Parse RFC 3339 date string to datetime object"
    if isinstance(dt_str, datetime):
        return dt_str

    if not dt_str:
        return None

    if dt_str.endswith("Z"):
        dt_str = LAST_Z_REGEX.sub("+00:00", dt_str)

    with suppress(ValueError):
        datetime.fromisoformat(dt_str)

    for fmt in (
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ):
        with suppress(ValueError):
            return datetime.strptime(dt_str, fmt)


_DT = TypeVar("_DT", bound=Mapping)


def convert_dict_items_to_datetime(keys: Sequence[str], data: _DT) -> _DT:
    "Convert mapping's items to datetime"

    def apply_parse(x: Tuple):
        if x[0] not in keys or not isinstance(x[1], str):
            return x
        return (x[0], parse_rfc3339(x[1]))

    return cast(_DT, dict(map(apply_parse, deepcopy(data).items())))


dict_dt_from_dt_str = partial(
    convert_dict_items_to_datetime, ["createdAt", "updatedAt"]
)


def is_metis_errors_evt_dto(evt: MetisEventDTO) -> TypeGuard[MetisErrorEventDTO]:
    "MetisEventDTO type guard"
    return bool(evt["type"] == "errors" and evt.get("data"))


def is_metis_error_dto(something) -> TypeGuard[MetisErrorDTO]:
    "MetisErrorDTO type guard"
    return (
        isinstance(something, dict)
        and "status" in something
        and "error" in something
        and (
            isinstance(something["error"], str)
            or isinstance(something["error"], dict)
            and "message" in something["error"]
            and something["error"]["message"]
        )
    )


def http_to_metis_error_map(status: int) -> Type[MetisError]:
    "Map HTTP exception to MetisError"
    err = MetisError
    if status in (HTTPForbidden.status_code, HTTPUnauthorized.status_code):
        err = MetisAuthenticationException
    if status == HTTPNotFound.status_code:
        err = MetisNotFoundException
    if status == HTTPBadRequest.status_code:
        err = MetisPayloadException
    if status == HTTPPaymentRequired.status_code:
        err = MetisQuotaException
    if status == HTTPMisdirectedRequest.status_code:
        err = MetisError
    return err


def metis_error_to_raise(dto: MetisErrorDTO):
    "Raise MetisErrorDTO"
    if isinstance(dto["error"], dict):
        msg = str(dto["error"]["message"])
    else:
        msg = dto["error"]
    err = http_to_metis_error_map(dto["status"])
    raise err(status=dto["status"], message=msg)


def raise_on_metis_error(func):
    "Raise on MetisErrorDTO in result"

    @wraps(func)
    async def wrapped(*args, **kwargs):
        result = await func(*args, **kwargs)
        if is_metis_error_dto(result):
            metis_error_to_raise(result)

        return result

    return wrapped


def raise_on_metis_error_in_event(func):
    "Raise on MetisErrorDTO in MetisEventDTO"

    @wraps(func)
    async def wrapped(*args, **kwargs):
        result = await func(*args, **kwargs)
        if is_metis_errors_evt_dto(result):
            errors = result.get("data", {}).get("data", [])
            if errors:
                metis_error_to_raise(errors[-1])

        return result

    return wrapped
