import logging
from logging import Logger
from typing import ClassVar, Optional, Any, Literal
from urllib.parse import quote

from .utils import MISSING

_log: Logger = logging.getLogger(__name__)

Method = Literal["GET", "POST", "PUT", "DELETE"]


def _set_api_environment(*, host: str = "njuns.com", app: str = "app") -> None:
    """Alter the :class:`Route` API environment. Defaults to the production environment.

    :param host: The host to connect to.
    :type host: str
    :param app: The app instance name to use.
    :type app: str
    """
    _log.info(f"Setting base API environment to {host}/{app}...")
    Route.BASE = f"https://{host}/{app}/rest/v2"


class Route:
    """Represents an API route/URL path"""

    BASE: ClassVar[str] = "https://njuns.com/app/rest/v2"

    def __init__(self, method: Method, path: str, /, **params: Any) -> None:
        """Initializes a whole route to an API endpoint.

        :param method: The HTTP method used to make the request.
        :type method: str
        :param path: The path to the endpoint.
        :type path: str
        :param params: The parameters for the endpoint URL
        :type params: Optional[dict]
        """
        self.path: str = path
        self.method: Method = method

        url = self.BASE + self.path
        # Assemble URL with parameters if present
        if params:
            url = url.format_map(
                {k: quote(v) if isinstance(v, str) else v for k, v in params.items()}
            )
        self.url: str = url

    def __str__(self) -> str:
        return f"{self.method} {self.url}"

    @staticmethod
    def assemble_params(*_, **kwargs) -> str:
        params = "&".join(
            map(
                lambda kv: f"{kv[0]}={kv[1]}",
                filter(lambda _kv: _kv[1] is not MISSING, kwargs.items()),
            )
        )
        if params:
            return f"?{params}"
        else:
            return ""
