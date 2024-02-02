"""Small helpers"""

import json
import re
import sys
from contextlib import suppress
from copy import deepcopy
from datetime import datetime
from functools import wraps
from typing import Any, Optional, Type, TypeVar

from aiohttp.web_exceptions import (
    HTTPBadRequest,
    HTTPForbidden,
    HTTPMisdirectedRequest,
    HTTPNotFound,
    HTTPPaymentRequired,
    HTTPUnauthorized,
)
from camel_converter import dict_to_camel, dict_to_snake

from .dtos import (
    MetisErrorDTO,
    MetisErrorEventDataDTO,
    MetisErrorEventDTO,
    MetisErrorMessageDTO,
)
from .exc import (
    MetisAuthenticationException,
    MetisError,
    MetisNotFoundException,
    MetisPayloadException,
    MetisQuotaException,
)

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
        return datetime.fromisoformat(dt_str)

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


_DT = TypeVar("_DT", bound=dict)


def convert_dict_values_to_dt(data: _DT) -> _DT:
    "Converts dictionary values to datetime"

    converted = deepcopy(data)
    for key, val in data.items():
        if isinstance(val, str):
            converted[key] = parse_rfc3339(val) or val
        elif isinstance(val, dict):
            converted[key] = convert_dict_values_to_dt(val)
        elif isinstance(val, list):
            converted[key] = [
                convert_dict_values_to_dt(x) if isinstance(x, dict) else x for x in val
            ]
        elif isinstance(val, tuple):
            converted[key] = tuple(
                convert_dict_values_to_dt(x) if isinstance(x, dict) else x for x in val
            )

    return converted


def convert_dict_values_from_dt(data: _DT) -> _DT:
    "Converts dictionary values from datetime to string"

    converted = deepcopy(data)
    for key, val in data.items():
        if isinstance(val, datetime):
            converted[key] = val.isoformat()
        elif isinstance(val, dict):
            converted[key] = convert_dict_values_from_dt(val)
        elif isinstance(val, list):
            converted[key] = [
                convert_dict_values_from_dt(x) if isinstance(x, dict) else x
                for x in val
            ]
        elif isinstance(val, tuple):
            converted[key] = tuple(
                convert_dict_values_from_dt(x) if isinstance(x, dict) else x
                for x in val
            )

    return converted


def metis_json_decoder(obj, *args, **kwargs):
    "Json decoder but with conversion to snake case and datetime"
    payload = json.loads(obj, *args, **kwargs)
    if isinstance(payload, dict):
        return convert_dict_values_to_dt(dict_to_snake(payload))
    return payload


def metis_json_encoder(obj, *args, **kwargs):
    "Json encoder but with conversion to camel case"
    payload = obj
    if isinstance(obj, dict):
        payload = convert_dict_values_from_dt(dict_to_camel(obj))
    return json.dumps(payload, *args, **kwargs)


def is_metis_error_error_dto(something) -> TypeGuard[MetisErrorMessageDTO]:
    "MetisErrorMessageDTO type guard"
    return (
        isinstance(something, dict)
        and "message" in something
        and isinstance(something["message"], str)
    )


def is_metis_error_dto(something) -> TypeGuard[MetisErrorDTO]:
    "MetisErrorDTO type guard"
    return (
        isinstance(something, dict)
        and "status" in something
        and "error" in something
        and (
            isinstance(something["error"], str)
            or is_metis_error_error_dto(something["error"])
        )
    )


def is_metis_error_event_data_dto(something) -> TypeGuard[MetisErrorEventDataDTO]:
    "MetisErrorEventDataDTO type guard"
    return (
        isinstance(something, dict)
        and "req_id" in something
        and "data" in something
        and isinstance(something["data"], list)
        and all(is_metis_error_dto(x) for x in something["data"])
    )


def is_metis_errors_evt_dto(something) -> TypeGuard[MetisErrorEventDTO]:
    "MetisEventDTO type guard"
    return (
        isinstance(something, dict)
        and something.get("type") == "errors"
        and "data" in something
        and is_metis_error_event_data_dto(something["data"])
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
    if isinstance(dto["error"], str):
        msg = dto["error"]
    else:
        msg = dto["error"]["message"]
    err = http_to_metis_error_map(dto.get("status"))
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
