import logging
from logging import Logger

from .http import HTTPClient
from .models.user import UserInfo
from .route import _set_api_environment
from .utils import MISSING, setup_logging

_log: Logger = logging.getLogger(__name__)
__all__ = "NJUNSClient"


class NJUNSClient(HTTPClient):
    """
    The NJUNS OAuth Client that handles the current session and authentication as well as requests to endpoints.
    """

    def __init__(self, *, log_level: int = logging.INFO) -> None:
        """Represents a client connection that connects to NJUNS."""
        setup_logging(level=log_level)
        super().__init__()

        self.user_info: UserInfo = MISSING

    async def login(
        self, *, username: str, password: str, use_uat_environment: bool = False
    ) -> None:
        """An asynchronous call that logs in with the provided username and password.

        :param username: The username to authenticate with.
        :type username: str
        :param password: The password to authenticate with.
        :type password: str
        :param use_uat_environment: Whether to use UAT environment or stay on production.
        :type use_uat_environment: bool
        :rtype: None
        """

        _log.info("Logging in to NJUNS API...")

        if not isinstance(username, str) or not isinstance(password, str):
            raise TypeError(
                f"Expected username or password to be a string, "
                f"got username:{username.__class__.__name__}, password:{password.__class__.__name__} instead"
            )

        if use_uat_environment:
            _set_api_environment(host="test.njuns.com", app="app2018")

        # Try to log in
        await self._static_login(username=username.strip(), password=password.strip())

        # Fetch user info after logging in
        self.user_info = await self.fetch_user_info()
