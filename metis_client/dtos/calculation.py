"""Calculation DTOs"""

from ..compat import NotRequired, Sequence
from .base import MetisTimestampsDTO
from .datasource import MetisDataSourceDTO


class MetisCalculationDTO(MetisTimestampsDTO):
    "Calculation DTO"
    id: int
    name: str
    user_id: int
    progress: int
    parent: int
    result: NotRequired[Sequence[MetisDataSourceDTO]]
