from typing import Any, Iterable, Type, TypeVar

from httpx import AsyncClient, HTTPError, Response
from loguru import logger
from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential

from lite_telegram.exceptions import TelegramException
from lite_telegram.models import Message, TelegramResponse, Update

T = TypeVar("T", bound=BaseModel)

BASE_URL_TEMPLATE = "https://api.telegram.org/bot{token}/"


class TelegramBot:
    """A Telegram bot.

    Args:
        client: The client to use for the bot.
        token: The token to use for the bot.
        timeout: The timeout to use for the bot.

    Example:
        >>> async with httpx.AsyncClient() as client:
        >>>     bot = TelegramBot(client, "YOUR_BOT_TOKEN")
        >>>     await bot.send_message(chat_id=1234567890, text="Hello, world!")
    """

    def __init__(self, client: AsyncClient, token: str, timeout: int = 60) -> None:
        self.client = client
        self.__token = token
        self.timeout = timeout

        self.__base_url = BASE_URL_TEMPLATE.format(token=self.__token)
        self._offset = 0

    async def get_me(self) -> Any:
        """Get the bot's information.

        Returns:
            The bot's information.
        """
        return await self._request(endpoint="getMe")

    async def send_message(self, chat_id: int, text: str) -> Message:
        """Send a message to a chat with the bot.

        Args:
            chat_id: The ID of the chat to send the message to.
            text: The text of the message to send.

        Returns:
            The sent message.
        """
        endpoint = "sendMessage"
        data = {"chat_id": chat_id, "text": text}

        logger.info("Sending message to {}: '{}'.", chat_id, text)
        resp_data = await self._request(endpoint=endpoint, data=data)
        return self._validate_model(resp_data, Message)

    async def get_updates(
        self, timeout: int = 300, allowed_updates: list[str] | None = None
    ) -> list[Update]:
        """Get updates from the bot.

        Args:
            timeout: The timeout to use for the request.
            allowed_updates: The allowed updates to get. Values: "message", "edited_message",
                "channel_post", "edited_channel_post".

        Returns:
            The updates.

        Example:
            >>> updates = await bot.get_updates()
            >>> for update in updates:
            >>>     print(update.message.text)
        """
        endpoint = "getUpdates"
        data: dict[str, Any] = {"timeout": timeout, "offset": self._offset}
        if allowed_updates is not None:
            data["allowed_updates"] = allowed_updates
        request_timeout = self.timeout + timeout

        resp_data = await self._request(endpoint=endpoint, data=data, timeout=request_timeout)
        updates = [self._validate_model(data, Update) for data in resp_data]
        self._update_offset(updates)
        return updates

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2),
        reraise=True,
    )
    async def _request(
        self, endpoint: str, data: dict[str, Any] | None = None, timeout: int | None = None
    ) -> Any:
        method = "POST"
        url = self.__base_url + endpoint
        timeout = timeout if timeout is not None else self.timeout

        logger.debug(
            "Sending request to telegram: method - '{}', url - '{}', timeout - '{}'.",
            method,
            url.replace(self.__token, "********"),
            timeout,
        )
        if data is not None:
            logger.debug("Request data: '{}'.", data)

        try:
            response = await self.client.request(method, url, data=data, timeout=timeout)
        except HTTPError as exc:
            raise TelegramException("Request to telegram api failed.") from exc

        return self._parse_result(response)

    def _parse_result(self, response: Response) -> Any:
        if not response.is_success:
            raise TelegramException(f"Received failed status code: {response.status_code}.")

        resp_data = self._validate_model(response.json(), TelegramResponse)
        if not resp_data.ok:
            raise TelegramException(f"Received failed response: {resp_data.result}.")
        return resp_data.result

    @staticmethod
    def _validate_model(data: dict[str, Any], model: Type[T]) -> T:
        try:
            return model.model_validate(data)
        except ValidationError as exc:
            raise TelegramException(exc) from exc

    def _update_offset(self, updates: Iterable[Update]) -> None:
        self._offset = max((update.update_id + 1 for update in updates), default=self._offset)
