import asyncio
from datetime import datetime

from lite_telegram.context import Context
from lite_telegram.types import FilterCallable


async def sleep_until(dt: datetime) -> None:
    sleep_time = dt - datetime.now()
    await asyncio.sleep(sleep_time.seconds)


def allowed_chats(chat_ids: int | str | list[int | str]) -> FilterCallable:
    if isinstance(chat_ids, (int, str)):
        chat_ids = [chat_ids]

    chat_ids = [int(chat_id) for chat_id in chat_ids]

    async def wrapper(ctx: Context) -> bool:
        return ctx.update.message is not None and ctx.update.message.chat.id in chat_ids

    return wrapper
