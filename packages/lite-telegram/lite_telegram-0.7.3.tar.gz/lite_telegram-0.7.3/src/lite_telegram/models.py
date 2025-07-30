from typing import Any, Literal

from pydantic import BaseModel


class TelegramResponse(BaseModel):
    ok: bool
    result: Any


class Chat(BaseModel):
    id: int
    type: Literal["private", "group", "supergroup", "channel"]


class Message(BaseModel):
    message_id: int
    chat: Chat
    text: str | None = None


class Update(BaseModel):
    update_id: int
    message: Message | None = None
