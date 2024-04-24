from typing import Optional

from aiohttp import ClientResponse

from .route import Route


class HTTPException(Exception):
    """Raised when an HTTP request returns a non-200 status code."""

    def __init__(
        self,
        message: str,
        route: Route,
        response: Optional[ClientResponse],
        content: Optional[str],
    ):
        self.route = route
        self.message = message
        self.response = response
        self.content = content

        super().__init__(
            "{}: {} {} - {}".format(
                self.message,
                self.response.status if self.response else "None",
                self.route,
                self.content,
            )
        )


class AuthenticationException(HTTPException):
    """Raised when an HTTP request failed while authenticating."""

    pass


class ServerError(HTTPException):
    """Raised when an HTTP request returns a 500 status code"""

    pass


class Forbidden(HTTPException):
    """Raised when an HTTP request returned a 403 status code."""

    pass


class NotFound(HTTPException):
    """Raised when an HTTP request returns a 404 status code."""

    pass
