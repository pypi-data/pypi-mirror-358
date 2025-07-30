from typing import Any


class XifyError(Exception):
    """Base exception class for all Xify-related errors."""

    pass


class AuthError(XifyError):
    """Raised for authentication-related errors."""

    pass


class APIError(XifyError):
    """Raised for errors returned by the X API."""

    def __init__(self, message: str, response: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.response = response


class RequestError(XifyError):
    """Raised for errors during the HTTP request process."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
