"""Small helpers"""

import re
from contextlib import suppress
from datetime import datetime
from typing import Optional

LAST_Z_REGEX = re.compile(r"Z$", re.IGNORECASE)


def parse_rfc3339(dt_str: Optional[str]) -> Optional[datetime]:
    "Parse RFC 3339 date string to datetime object"
    if not dt_str:
        return None
    with suppress(ValueError):
        return datetime.fromisoformat(LAST_Z_REGEX.sub("+00:00", dt_str))
    with suppress(ValueError):
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    with suppress(ValueError):
        # Perhaps the datetime has a whole number of seconds with no decimal
        # point. In that case, this will work:
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S%z")
