import asyncio
import base64
import json
import logging
import socket
import sys
from datetime import datetime, timedelta
from logging import Logger
from typing import Optional, Any, Dict, Union

import aiohttp
from aiohttp import TCPConnector

from .exceptions import (
    AuthenticationException,
    HTTPException,
    Forbidden,
    NotFound,
    ServerError,
)
from .models.user import UserInfo
from .route import Route
from .routes.entities import EntitiesRoute
from .routes.queries import QueriesRoute
from .utils import MISSING, Response

_log: Logger = logging.getLogger(__name__)


async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    """Takes in a response from aiohttp and returns the data as a string or dictionary

    :param response: The :class:`aiohttp.ClientResponse` instance.
    :type response: aiohttp.ClientResponse
    :return: The response contents as a string or a dictionary.
    :rtype: Union[Dict[str, Any], str]
    """
    text = await response.text(encoding="utf-8")
    try:
        if "application/json" in response.headers["Content-Type"]:
            return json.loads(text)
    except KeyError:
        pass
    return text


class HTTPClient(EntitiesRoute, QueriesRoute):
    """Represents an HTTP client sending requests to the NJUNs API"""

    def __init__(self):
        super().__init__(self)
        self.__access_token: Optional[str] = None
        self.__refresh_token: Optional[str] = None
        self.__expires_in: Optional[datetime] = None
        self.__scope: Optional[str] = None

        self.__user_agent: str = (
            "TechServ (https://techserv.com/) Python/{0[0]}.{0[1]} aiohttp/{1}".format(
                sys.version_info, aiohttp.__version__
            )
        )
        self.__session: aiohttp.ClientSession = MISSING  # gets set in static_login

        _log.info(
            "Initialized HTTP client, using API base URL: {}".format(Route("", ""))
        )

    async def _static_login(
        self,
        *,
        username: Optional[str] = MISSING,
        password: Optional[str] = MISSING,
        refresh_token: Optional[str] = MISSING,
        grant_type: str = "password",
    ) -> Response:
        """Initializes the HTTP session, attempts to log in with the provided creds, then stores the tokens for this session.

        :param username:
        :param password:
        :param refresh_token:
        :param grant_type:
        :return:
        """
        if self.__session is MISSING:
            self.__session = aiohttp.ClientSession(
                connector=TCPConnector(limit=0, family=socket.AF_INET)
            )

        route: Route = Route(
            "POST",
            "/oauth/token?grant_type={{grant_type}}{}{}{}".format(
                "&username={username}" if username is not MISSING else "",
                "&password={password}" if password is not MISSING else "",
                (
                    "&refresh_token={refresh_token}"
                    if refresh_token is not MISSING
                    else ""
                ),
            ),
            username=username if username is not MISSING else None,
            password=password if password is not MISSING else None,
            refresh_token=refresh_token if refresh_token is not MISSING else None,
            grant_type=grant_type,
        )

        if grant_type != "refresh_token" and refresh_token is not MISSING:
            raise ValueError("Invalid grant_type with refresh_token provided.")

        if (
            refresh_token is not MISSING
            and username is not MISSING
            and password is not MISSING
        ):
            raise ValueError(
                "Cannot provide both refresh_token and username and password."
            )

        try:
            data = await self.request(
                route,
                headers=(
                    {
                        "Authorization": "Basic "
                        + base64.b64encode("client:secret".encode()).decode()
                    }
                    if refresh_token is MISSING
                    else None
                ),
            )

            self.__access_token = data["access_token"]
            self.__refresh_token = data["refresh_token"]
            self.__expires_in = datetime.now() + timedelta(
                seconds=int(data["expires_in"])
            )
            self.__scope = data["scope"]
        except HTTPException as e:
            if e.response.status == 400:
                raise AuthenticationException(
                    "Authentication failed, ex. invalid CUBA username or password.",
                    route,
                    e.response,
                    await e.response.text(),
                )
            if e.response.status == 401:
                raise AuthenticationException(
                    "Basic authentication failed",
                    route,
                    e.response,
                    await e.response.text(),
                )

            # Reraise if other than failed authentication
            raise e
        return data

    async def close(self):
        """Ensure that the :class:`aiohttp.ClientSession` instance is closed.

        The user should call this in their script."""
        await self.__session.close()
        self.__session = MISSING

    async def request(self, route: Route, *_, **kwargs: Any) -> Response:
        method: str = route.method
        url: str = route.url

        headers: Dict[str, str] = {"User-Agent": self.__user_agent}

        # Append token if present
        if self.__access_token is not None:
            if self.__expires_in <= datetime.now():
                # The NJUNS API docs has no entries for refreshing a token, but I'm just going to follow OAuth standards and pray

                _log.warning("Access token expired, requesting a refresh...")

                # Reset expires_at so the request method can successfully call a request and return the response.
                # Otherwise, this would result in an infinite loop.
                self.__expires_in = datetime.now() + timedelta(seconds=3600)

                # Send a request for a new token using the refresh token.
                await self._static_login(
                    username=None,
                    password=None,
                    refresh_token=self.__refresh_token,
                    grant_type="refresh_token",
                )

            # If an access token is present, assign it in the headers
            headers["Authorization"] = f"Bearer {self.__access_token}"

        # Check if it's a JSON request
        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = json.dumps(kwargs.pop("json"))
        else:
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        # Update headers with overridden ones from kwargs
        if "headers" in kwargs and isinstance(kwargs["headers"], dict):
            headers.update(kwargs["headers"])

        # Assign headers to kwargs, so it can be passed in the below request call
        kwargs["headers"] = headers

        response: Optional[aiohttp.ClientResponse] = None

        for tries in range(5):
            try:
                _log.debug(kwargs)
                async with self.__session.request(method, url, **kwargs) as response:
                    _log.debug(
                        "{} {} ({}) -> {}".format(
                            method, url, kwargs.get("data"), response.status
                        )
                    )

                    data: Optional[Union[Dict[str, Any], str]] = await json_or_text(
                        response
                    )

                    if 300 > response.status >= 200:
                        # Successful response, return data
                        _log.debug("{} {} -> {}".format(method, url, data))
                        return data

                    if response.status == 429:
                        # Rate limited, try again after a delay
                        _log.debug("{} {} -> {}".format(method, url, data))
                        _log.error(
                            "{} {} - Rate limited, trying again in 3 seconds".format(
                                method, url
                            )
                        )
                        await asyncio.sleep(3)
                        continue

                    if response.status in (500, 502, 504, 524) and not (
                        isinstance(data, dict) and "error" in data
                    ):
                        # Server error, try again after a delay
                        _log.error(
                            "{} {} - Server error, trying again in {} seconds".format(
                                method, url, (1 + tries * 2)
                            )
                        )
                        await asyncio.sleep(1 + tries * 2)
                        continue

                    # Errors for other cases that should not be retried
                    if response.status == 403:
                        raise Forbidden(
                            "Access is denied", route, response, await response.text()
                        )
                    elif response.status == 404:
                        raise NotFound(
                            "Not found", route, response, await response.text()
                        )
                    elif response.status >= 500:
                        raise ServerError(
                            "Server error", route, response, await response.text()
                        )
                    else:
                        raise HTTPException(
                            "Request failed", route, response, await response.text()
                        )
            except OSError as e:
                # Socket error, try again if possible
                if tries < 4 and e.errno in (54, 10054):
                    await asyncio.sleep(1 + tries * 2)
                    continue
                raise
        if response is not None:
            if response.status >= 500:
                raise ServerError(
                    "Server error", route, response, await response.text()
                )

            raise HTTPException(
                "Request failed", route, response, await response.text()
            )

        raise RuntimeError("Unreachable code in HTTP handler")

    async def fetch_user_info(self, /) -> UserInfo:
        """Fetches the currently logged-in user"""
        return UserInfo(**await self.request(Route("GET", "/userInfo")))
