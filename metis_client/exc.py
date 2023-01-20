"""Custom exceptions for metis_client."""


from aiohttp import ClientResponseError


class MetisException(BaseException):
    """
    This is raised when unknown exceptions occour.
    And it's used as a base for all other exceptions
    so if you want to catch all Metis related errors
    you should catch this base exception.
    """

    error: str | None

    def __init__(self, *args, error: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.error = error


class MetisConnectionException(MetisException):
    """This is raised when there is a connection issue with Metis."""


class MetisHttpResponseError(MetisException, ClientResponseError):
    """Base for all HTTP errors"""


class MetisNotFoundException(MetisHttpResponseError):
    """This is raised when the requested resource is not found."""


class MetisPayloadException(MetisHttpResponseError):
    """This is raised when the payload is invalid."""


class MetisPermissionException(MetisHttpResponseError):
    """This is raised when the user has no permission to do the requested resource."""


class MetisAuthenticationException(MetisHttpResponseError):
    """This is raised when we recieve an authentication issue."""

class MetisQuotaException(MetisHttpResponseError):
    """This is raised when quota excided."""
