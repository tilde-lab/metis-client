"Base response DTO"

import sys

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import TypedDict
else:  # pragma: no cover
    from typing import TypedDict


class MetisRequestIdDTO(TypedDict):
    "Response with request id dictionary"
    reqId: str
