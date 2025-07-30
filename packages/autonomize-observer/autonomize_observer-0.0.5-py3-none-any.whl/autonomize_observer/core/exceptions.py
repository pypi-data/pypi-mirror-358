"""Custom exceptions for the ML Observability SDK."""

# Import available exceptions from autonomize-core
from autonomize.exceptions.core import (
    ModelhubMissingCredentialsException,
    ModelhubUnauthorizedException,
    ModelhubInvalidTokenException,
    ModelhubTokenRetrievalException,
)


class MLObservabilityException(Exception):
    """Base exception for all custom errors in the ml-observability library."""

    pass


# Additional exceptions needed for ML Observability that aren't in autonomize-core
class ModelHubAPIException(Exception):
    """Exception for ModelHub API errors."""

    pass


class ModelHubBadRequestException(ModelHubAPIException):
    """Exception for ModelHub bad request errors."""

    pass


class ModelHubConflictException(ModelHubAPIException):
    """Exception for ModelHub conflict errors."""

    pass


class ModelHubResourceNotFoundException(ModelHubAPIException):
    """Exception for ModelHub resource not found errors."""

    pass


# Re-export for backward compatibility
__all__ = [
    "MLObservabilityException",
    "ModelHubAPIException",
    "ModelHubBadRequestException",
    "ModelHubConflictException",
    "ModelHubResourceNotFoundException",
    "ModelhubMissingCredentialsException",
    "ModelhubUnauthorizedException",
    "ModelhubInvalidTokenException",
    "ModelhubTokenRetrievalException",
]
