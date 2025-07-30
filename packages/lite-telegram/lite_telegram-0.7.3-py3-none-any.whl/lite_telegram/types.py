from typing import Awaitable, Callable

from lite_telegram.bot import TelegramBot
from lite_telegram.context import Context

FilterCallable = Callable[[Context], Awaitable[bool]]
HandlerCallable = Callable[[Context], Awaitable[None]]
ScheduleCallable = Callable[[TelegramBot], Awaitable[None]]
