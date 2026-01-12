"""Error handling utilities (RFC 7807 Problem Details)."""

from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """RFC 7807 Problem Details response model."""

    type: str = "about:blank"
    title: str
    detail: str | None = None
    status: int
    extensions: dict[str, Any] | None = None


class ErrorResponseFactory:
    """Factory for creating standardized error responses."""

    # Status code to user-friendly message mapping
    STATUS_MESSAGES: dict[int, tuple[str, str]] = {
        400: ("Invalid Request", "Please check your input and try again."),
        401: ("Session Expired", "Please sign in again to continue."),
        403: ("Access Denied", "You don't have permission to access this resource."),
        404: ("Not Found", "The requested resource was not found."),
        429: ("Too Many Requests", "Please wait a moment and try again."),
        500: ("Service Temporarily Unavailable", "We're experiencing technical difficulties. Please try again later."),
        503: ("Service Unavailable", "The service is temporarily unavailable."),
    }

    @classmethod
    def create(
        cls,
        status_code: int,
        detail: str | None = None,
        include_extensions: bool = False,
        exception: Exception | None = None,
    ) -> ErrorResponse:
        """
        Create an error response for the given status code.

        Args:
            status_code: HTTP status code
            detail: Optional detail message (overrides default)
            include_extensions: Include debug info (development only)
            exception: Optional exception for debug info

        Returns:
            ErrorResponse instance
        """
        title, default_detail = cls.STATUS_MESSAGES.get(
            status_code,
            ("Error", "An unexpected error occurred."),
        )

        extensions = None
        if include_extensions and exception:
            extensions = {
                "exceptionType": type(exception).__name__,
                "exceptionMessage": str(exception),
            }

        return ErrorResponse(
            title=title,
            detail=detail or default_detail,
            status=status_code,
            extensions=extensions,
        )

    @classmethod
    def from_exception(
        cls,
        exception: Exception,
        status_code: int = 500,
        is_development: bool = False,
    ) -> ErrorResponse:
        """
        Create an error response from an exception.

        Args:
            exception: The exception that occurred
            status_code: HTTP status code
            is_development: Include debug info if True

        Returns:
            ErrorResponse instance
        """
        detail = str(exception) if is_development else None
        return cls.create(
            status_code=status_code,
            detail=detail,
            include_extensions=is_development,
            exception=exception,
        )
