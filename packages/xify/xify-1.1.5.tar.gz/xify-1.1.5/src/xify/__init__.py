import logging
from types import TracebackType
from typing import Any, cast

from .errors import XifyError
from .handlers.auth import AuthHandler
from .handlers.request import RequestHandler

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Xify:
    """A Python client library for interacting with the X API.

    This library provides tools to authenticate, make requests, and
    process responses from the X API, simplifying a common task such as
    posting and deleting tweets.
    """

    def __init__(
        self,
        consumer_key: str | None,
        consumer_secret: str | None,
        access_token: str | None,
        access_token_secret: str | None,
    ) -> None:
        """Initialize the Xify instance.

        Args:
            consumer_key (str | None): X API consumer key. Defaults to
                None.
            consumer_secret (str | None): X API consumer secret.
                Defaults to None.
            access_token (str | None): X API access token. Defaults to None.
            access_token_secret (str | None): X API access token
                secret. Defaults to None.
        """
        self._auth = AuthHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )
        self._request = RequestHandler(self._auth)

        logger.debug("Xify instance has been initialized.")

    async def __aenter__(self) -> "Xify":
        """Enter the async context manager and initialize the session.

        Returns:
            self: The current Xify instance.
        """
        logger.debug("Entering async context.")
        await self._request.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the async context manager and close the session."""
        logger.debug("Exiting async context.")
        await self._request.disconnect()

    async def tweet(self, content: dict[str, Any]) -> dict[str, Any]:
        """Send a tweet.

        Args:
            content (Dict[str, Any]): The content of the tweet.

        Raises:
            XifyError: If an error arises while sending tweet.

        Returns:
            Dict[str, Any]: The data of the sent tweet.
        """
        logger.debug("Attempting to post a tweet.")

        try:
            url = "https://api.twitter.com/2/tweets"
            payload = {}

            if "msg" in content:
                payload["text"] = content["msg"]

            response = await self._request.send("POST", url, json_body=payload)
            data = response.get("data", {})

            logger.info("Tweet posted successfully: %s", data)
            return cast(dict[str, Any], data)

        except Exception as e:
            if isinstance(e, XifyError):
                raise

            raise XifyError(
                f"An unexpected error occurred while sending tweet: {e}"
            ) from e
