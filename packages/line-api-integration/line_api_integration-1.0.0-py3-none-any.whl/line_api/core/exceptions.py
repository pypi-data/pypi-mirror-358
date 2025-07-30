"""Custom exceptions for LINE API integration."""

from __future__ import annotations


class LineAPIError(Exception):
    """Base exception for all LINE API related errors."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            error_code: Optional error code from LINE API

        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class LineConfigError(LineAPIError):
    """Exception raised for configuration related errors."""


class LineMessageError(LineAPIError):
    """Exception raised for messaging related errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        """
        Initialize the messaging error.

        Args:
            message: Human-readable error message
            error_code: Optional error code from LINE API
            status_code: HTTP status code from the response
            response_body: Response body from LINE API

        """
        super().__init__(message, error_code)
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self) -> str:
        """Return string representation of the error."""
        parts: list[str] = []
        if self.error_code:
            parts.append(f"[{self.error_code}]")
        if self.status_code:
            parts.append(f"HTTP {self.status_code}")
        parts.append(self.message)
        return " ".join(parts)


class LineRateLimitError(LineMessageError):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
    ) -> None:
        """
        Initialize the rate limit error.

        Args:
            message: Human-readable error message
            retry_after: Seconds to wait before retrying

        """
        super().__init__(message)
        self.retry_after = retry_after


class LineValidationError(LineAPIError):
    """Exception raised for validation errors."""


class LineTimeoutError(LineAPIError):
    """Exception raised for timeout errors."""
