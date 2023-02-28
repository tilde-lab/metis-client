"""Calculation DTOs"""
import sys

from .base import MetisTimestampsDTO
from .datasource import MetisDataSourceDTO

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Sequence
else:  # pragma: no cover
    from collections.abc import Sequence

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import NotRequired
else:  # pragma: no cover
    from typing import NotRequired


class MetisCalculationDTO(MetisTimestampsDTO):
    "Calculation DTO"
    id: int
    name: str
    userId: int
    status: int
    progress: int
    result: NotRequired[Sequence[MetisDataSourceDTO]]
