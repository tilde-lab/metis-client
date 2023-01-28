"""Base class for all GitHub objects."""

from logging import Logger

from ..const import LOGGER


# pylint: disable=too-few-public-methods
class MetisBase:
    """Base class for all Metis objects."""

    logger: Logger = LOGGER
