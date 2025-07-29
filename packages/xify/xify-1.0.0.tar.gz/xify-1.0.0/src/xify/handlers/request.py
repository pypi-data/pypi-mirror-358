import logging
from http import HTTPStatus
from typing import Any, cast
from urllib.parse import parse_qs, urlparse

import aiohttp

from ..errors import APIError, RequestError, XifyError
from .auth import AuthHandler

logger = logging.getLogger(__name__)


class RequestHandler:
    def __init__(self, auth: AuthHandler) -> None:
        """Initialize the request handler.

        Args:
            auth (AuthHandler): The auth handler for signing requests.
        """
        self._auth = auth
        self._session: aiohttp.ClientSession | None = None

        logger.debug("Request handler instance has been initialized.")

    async def connect(self) -> None:
        """Create the aiohttp ClientSession."""
        if not self._session or self._session.closed:
            logger.debug("Attempting to create aiohttp.ClientSession.")
            self._session = aiohttp.ClientSession()
            logger.debug("aiohttp.ClientSession has been created.")

    async def disconnect(self) -> None:
        """Close the aiohttp ClientSession."""
        if self._session and not self._session.closed:
            logger.debug("Attempting to close aiohttp.ClientSession.")
            await self._session.close()
            logger.debug("aiohttp.ClientSession has been closed.")

        self._session = None

    def _create_request_arguements(
        self,
        http_method_upper: str,
        url: str,
        query_params: dict[str, str],
        form_body_params: dict[str, str],
        json_body: dict[str, str],
    ) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
        """Create and format the arguments for a request.

        Args:
            http_method_upper (str): The method of the HTTP request.
            url (str): The URL of the API endpoint.
            query_params (Dict[str, str]): The URL's query parameters.
            form_body_params (Dict[str, str]): The form body content.
            json_body (Dict[str, str]): The json body content.

        Raises:
            ValueError: If json_Body and form_body_params are given.

        Returns:
            Tuple[Dict[str, str], Dict[str, Dict[str, str]]]: The
                header and request kwargs needed to complete a request
                to the X API.
        """
        logger.debug("Creating request arguments for %s %s", http_method_upper, url)

        # Collect parameters for the OAuth signature
        parsed_url = urlparse(url)
        query_params_from_url = {k: v[0] for k, v in parse_qs(parsed_url.query).items()}

        params_for_signature = {
            **query_params_from_url,
            **query_params,
        }
        request_kwargs = {"params": {**query_params_from_url, **query_params}}
        headers = {}

        if http_method_upper in {"POST", "PUT", "PATCH"}:
            if json_body and form_body_params:
                raise ValueError("Cannot use both 'json_body' and 'form_body_params'.")

            if json_body:
                headers["Content-Type"] = "application/json"
                request_kwargs["json"] = json_body
            elif form_body_params:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                params_for_signature.update(form_body_params)
                request_kwargs["data"] = form_body_params

        # Create OAuth authorization string
        auth_str = self._auth.sign_request(http_method_upper, url, params_for_signature)
        headers["Authorization"] = auth_str

        return headers, request_kwargs

    async def _handle_error_response(self, response: aiohttp.ClientResponse) -> None:
        """Parse an error response and raise an appropriate APIError.

        Raises:
            APIError: If a response's status code is above 400.
        """
        logger.debug("Handling API error response. Status: %s", response.status)

        msg = f"API Error {response.status}"
        error_data = None
        try:
            error_data = await response.json()
            detail = error_data.get("detail", "No details provided.")
            msg += f": {detail}"
        except Exception:
            error_text = await response.text()
            msg += f": {error_text}"

        raise APIError(msg, response=error_data)

    async def _send_request(
        self,
        http_method_upper: str,
        url: str,
        headers: dict[str, str],
        request_kwargs: dict[str, dict[str, str]],
    ) -> dict[str, Any]:
        """Send a HTTP request to X's API.

        Args:
            http_method_upper (str): The method of the HTTP request.
            url (str): The URL of the API endpoint.
            headers (Dict[str, str]): The request argument to
                authenticate this request as well as include any
                necessary arguments.
            request_kwargs (Dict[str, Dict[str, str]]): Additional
                arguments that are needed for the request.

        Raises:
            RequestError: If a unsuccesful request attempt arises or if
                the ClientSession is not setup or open.

        Returns:
            Dict[str, Any]: The JSON response containing the data of
                the successful request.
        """
        try:
            if not self._session or self._session.closed:
                raise RequestError("ClientSession is not connected.")
            else:
                logger.debug(
                    "Sending request: %s %s, headers=%s, kwargs=%s",
                    http_method_upper,
                    url,
                    headers,
                    request_kwargs,
                )

                async with self._session.request(
                    http_method_upper, url, headers=headers, **request_kwargs
                ) as response:
                    logger.debug("Received response with status: %s", response.status)
                    if response.status >= HTTPStatus.BAD_REQUEST:
                        await self._handle_error_response(response)

                    return cast(dict[str, Any], await response.json())

        except aiohttp.ClientResponseError as e:
            raise RequestError(
                f"HTTP {e.status} {e.message} for {e.request_info.url}"
            ) from e

        except Exception as e:
            if isinstance(e, XifyError):
                raise
            raise RequestError("An error occurred while sending request.") from e

    async def send(
        self,
        http_method: str,
        url: str,
        query_params: dict[str, str] | None = None,
        form_body_params: dict[str, str] | None = None,
        json_body: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Handle sending HTTP requests with OAuth 1.0a authentication.

        Args:
            http_method (str): The method of the HTTP request.
            url (str): The URL of the API endpoint.
            query_params (dict | None, optional): The URL's query
                parameters. Defaults to None.
            form_body_params (dict | None, optional): The form body
                content. Defaults to None.
            json_body (dict | None, optional): The json body content.
                Defaults to None.

        Returns:
            Dict[str, Any]: The JSON response containing the data of
                the successful request.
        """
        if query_params is None:
            query_params = {}
        if form_body_params is None:
            form_body_params = {}
        if json_body is None:
            json_body = {}

        http_method_upper = http_method.upper()

        headers, request_kwargs = self._create_request_arguements(
            http_method_upper, url, query_params, form_body_params, json_body
        )

        return await self._send_request(http_method_upper, url, headers, request_kwargs)
