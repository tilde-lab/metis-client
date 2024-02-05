"Base response DTO"

from ..compat import TypedDict


class MetisRequestIdDTO(TypedDict):
    "Response with request id dictionary"
    req_id: str
