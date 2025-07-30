from typing import Any

from lite_telegram.bot import TelegramBot
from lite_telegram.exceptions import TelegramException
from lite_telegram.models import Message, Update


class Context:
    """A context for a Telegram update.

    Args:
        bot: The bot that received the update.
        update: The update that contains the message.
    """

    _params: dict[str, Any] = {}

    def __init__(self, bot: TelegramBot, update: Update) -> None:
        self.bot = bot
        self.update = update

    @property
    def is_text_message(self) -> bool:
        """Check if the update is a text message."""
        return self.update.message is not None and self.update.message.text is not None

    @property
    def is_command(self) -> bool:
        """Check if the update is a command."""
        return (
            self.update.message is not None
            and self.update.message.text is not None
            and self.update.message.text.startswith("/")
            and len(self.update.message.text) > 1
        )

    @property
    def is_private_chat(self) -> bool:
        """Check if the update is a private chat."""
        return self.update.message is not None and self.update.message.chat.type == "private"

    @property
    def text(self) -> str | None:
        """Get the text of the message if it is a text message and None otherwise."""
        return (
            self.update.message.text
            if self.update.message is not None and self.update.message.text is not None
            else None
        )

    @property
    def chat_id(self) -> int | None:
        """Get the chat id of the message if it is a message and None otherwise."""
        return self.update.message.chat.id if self.update.message is not None else None

    async def reply(self, text: str) -> Message:
        """Reply to the update message.

        Args:
            text: The text to reply with.

        Returns:
            The message that was sent.

        Raises:
            TelegramException: If the context is not a message.
        """
        if self.update.message is None:
            raise TelegramException("Context is not a message.")

        return await self.bot.send_message(self.update.message.chat.id, text)

    def set(self, key: str, value: Any) -> None:
        """Set a parameter for the context.

        Args:
            key: The key to set.
            value: The value to set.
        """
        self._params[key] = value

    def get(self, key: str) -> Any | None:
        """Get a parameter from the context.

        Args:
            key: The key to get.

        Returns:
            The value of the parameter or None if the key is not found.
        """
        return self._params.get(key)
