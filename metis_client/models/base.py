"""Base class for all GitHub objects."""

from logging import Logger

from ..const import LOGGER


class MetisBase:
    """Base class for all Metis objects."""

    logger: Logger = LOGGER
