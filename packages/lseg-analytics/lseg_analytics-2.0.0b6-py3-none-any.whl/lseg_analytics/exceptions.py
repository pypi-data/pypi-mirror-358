"""Public exceptions."""

from enum import Enum

import corehttp.exceptions

from lseg_analytics_basic_client.models import ServiceError, ServiceErrorResponse

__all__ = [
    "LibraryException",
    "ServerError",
    "ResourceNotFound",
    "GatewayError",
    "AuthenticationError",
    "ProxyStatusError",
    "ProxyNotEnabledError",
    "ProxyAuthFailureError",
    "ProxyNotFoundError",
]


class _ERROR_MESSAGE(Enum):
    PROXY_DISABLED = "Cannot connect to the LSEG Financial Analytics platform because seamless authentication is not enabled. Please enable it in the LSEG VS Code extension settings and try again."
    PROXY_UNAUTHORIZED = "Cannot connect to the LSEG Financial Analytics platform because you are not logged in to the extension. Please log in, and try again."
    PROXY_FORBIDDEN = "Cannot connect to the LSEG Financial Analytics platform because you are not authorized to the extension. Please contact the LSEG support team."
    NO_AVALIABLE_PORT = "Cannot connect to the LSEG Financial Analytics platform because the port number to enable seamless authentication was not found. Please try restarting VS Code or contact the LSEG support team if the problem persists."
    INVALID_RESPONSE = "Cannot connect to the LSEG Financial Analytics platform because there is an error with seamless authentication and the status of the extension cannot be retrieved. Please try restarting VS Code or contact the LSEG support team if the problem persists."
    CREDENTIAL_UNAUTHORIZED = "Cannot authenticate to the LSEG Financial Analytics platform. Please ensure your client id/password is configured correctly."
    GET_TOKEN_FAILED = "Cannot connect to the LSEG Financial Analytics platform because of a network or certification issue. Please check your network connection."
    PROXY_FAILURE = "Cannot connect to the LSEG Financial Analytics platform because there was an error with seamless authentication. Please try restarting VS Code or contact the LSEG support team if the problem persists."


class LibraryException(Exception):
    """Base class for all library exception, excluding azure ones"""


class ServerError(LibraryException):
    """Server error exception"""


class ProxyStatusError(LibraryException):
    """Proxy failed exception"""


class ProxyNotEnabledError(LibraryException):
    """Proxy not enabled exception"""


class ProxyNotFoundError(LibraryException):
    """Proxy not found exception"""


class ProxyAuthFailureError(LibraryException):
    """Proxy authentication or authorization exception"""


class ResourceNotFound(ServerError):
    """Resource not found exception"""


class GatewayError(LibraryException):
    """Gateway error exception"""


class AuthenticationError(GatewayError):
    """Authentication error exception"""


def check_and_raise(response):
    """Check server response and raise exception if needed"""
    if not isinstance(response, ServiceErrorResponse):
        return response
    if getattr(response, "error", None):
        if response.error.code.isdigit():  # Gateway error
            raise GatewayError(f"Gateway error: code={response.error.code} {response.error.message}")
        else:  # Server error
            if get_error_code(response).lower() == "not found":
                raise ResourceNotFound(f"Resource not found: code={response.error.code} {response.error.message}")
            else:
                raise ServerError(f"Server error: code={response.error.code} {response.error.message}")

    # Handle the temporary gateway error which contains only 'message' in response. To be removed after gateway fixed error schema.
    if getattr(response, "_data", None):
        if "meta" in response._data.keys():
            raise ServerError(f"Server error: {response._data}")
        elif "message" in response._data.keys():
            raise GatewayError(f"Gateway error: {response._data['message']}")
        else:
            raise GatewayError(f"Gateway error: {response._data}")
    else:
        raise ServerError(f"Server error: {response}")


def get_error_code(response: "ServiceErrorResponse") -> str:
    """Get error code from response

    We need this function because backend returns error code in different places at the moment
    """
    if response.error is None and isinstance(response.get("status"), int):
        return str(response["status"])
    elif response.error is None and "statusCode" in response:
        return str(response["statusCode"])
    elif response.error is not None:
        return response.error.status
    else:
        raise ValueError(f"Unexpected error response structure: {response}")


def check_exception_and_raise(error):
    if isinstance(error, corehttp.exceptions.ServiceRequestError):
        raise AuthenticationError(
            f"Cannot connect to the LSEG Financial Analytics platform because of a network or certification issue({error}). Please check your network connection."
        )
    # (ASDK-688)
    elif isinstance(error, corehttp.exceptions.DecodeError):
        if error.status_code == 504:
            raise ServerError(f"Server error: {error}")
        else:
            raise error
    # (ASDK-675 and ASDK-688)
    elif isinstance(error, corehttp.exceptions.HttpResponseError):
        if error.status_code == 502:
            raise GatewayError(f"Bad Gateway: {error}")
        elif error.status_code == 504:
            raise GatewayError(f"Gateway Timeout: {error}")
        else:
            raise error
    raise error


def check_id(id):
    """Check if id is None"""
    if id is None:
        raise LibraryException("Resource should be saved first before calling the method!")
