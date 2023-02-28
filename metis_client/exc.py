"""Custom exceptions for metis_client."""


from typing import Optional


class MetisException(BaseException):
    """
    This is raised when unknown exceptions occour.
    And it's used as a base for all other exceptions
    so if you want to catch all Metis related errors
    you should catch this base exception.
    """


class MetisConnectionException(MetisException):
    """This is raised when there is a connection issue with Metis."""


class MetisError(MetisException):
    """Base of all errors based on results"""

    status: int = 0
    message: Optional[str]

    def __init__(
        self, *args, status: Optional[int], message: Optional[str] = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        if status:
            self.status = status
        if message:
            self.message = message


class MetisNotFoundException(MetisError):
    """This is raised when the requested resource is not found."""


class MetisPayloadException(MetisError):
    """This is raised when the payload is invalid."""


class MetisPermissionException(MetisError):
    """This is raised when the user has no permission to do the requested resource."""


class MetisAuthenticationException(MetisError):
    """This is raised when we recieve an authentication issue."""


class MetisQuotaException(MetisError):
    """This is raised when quota excided."""
