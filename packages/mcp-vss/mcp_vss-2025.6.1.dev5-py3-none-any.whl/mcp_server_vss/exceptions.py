"""Exceptions for VSS API MCP server."""


class VssError(Exception):
    """Custom exception for VSS API errors."""

    def __init__(self, message: str):
        """Initialize the exception with a message."""
        self.message = message
        super().__init__(message)

    def __str__(self):
        """Return the message of the exception."""
        return self.message
