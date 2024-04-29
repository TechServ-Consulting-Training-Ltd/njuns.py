import logging
from abc import ABC
from logging import Logger
from typing import Any, Callable, Awaitable

from ..route import Route
from ..utils import Response

_log: Logger = logging.getLogger(__name__)


class BaseRoute(ABC):
    """Base class to be subclassed by individual routes."""

    def __init__(self, client: Any):
        """Initializes a route class by propagating the HTTPClient instance to the inheriting class.

        :param client: The :class:`HTTPClient` instance.
        """
        self.request: Callable[[Route, ...], Awaitable[Response]] = client.request
        _log.debug(f"Initializing {__name__}")
