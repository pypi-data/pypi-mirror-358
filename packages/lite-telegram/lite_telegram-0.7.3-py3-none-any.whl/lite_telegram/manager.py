import asyncio
from datetime import datetime
from typing import NamedTuple

from croniter import croniter
from loguru import logger

from lite_telegram.bot import TelegramBot
from lite_telegram.context import Context
from lite_telegram.types import FilterCallable, HandlerCallable, ScheduleCallable
from lite_telegram.utils import sleep_until


class Schedule(NamedTuple):
    cron: str
    task: ScheduleCallable


class BotManager:
    """A manager for a Telegram bot.

    Args:
        bot: The bot to manage.
        poll_interval: The interval to poll for updates.
        allowed_updates: The allowed updates to poll for.
    """

    def __init__(
        self,
        bot: TelegramBot,
        poll_interval: int = 60,
        allowed_updates: list[str] | None = None,
    ) -> None:
        self.bot = bot
        self.poll_interval = poll_interval
        self.allowed_updates = allowed_updates

        self._commands: dict[str, HandlerCallable] = {}
        self._text_handlers: list[HandlerCallable] = []
        self._filters: list[FilterCallable] = []
        self._schedules: list[Schedule] = []

    def add_command(self, command: str, handle: HandlerCallable) -> None:
        """Add a command handler.

        Args:
            command: The command to add.
            handle: The handler to add.

        Example:
            >>> manager.add_command("/start", start_command)
            >>> manager.add_command("/help", help_command)
        """
        self._commands[command] = handle

    def add_text_handler(self, handle: HandlerCallable) -> None:
        """Add a text handler.

        Args:
            handle: The handler to add.

        Example:
            >>> manager.add_text_handler(echo)
        """
        self._text_handlers.append(handle)

    def add_filter(self, filter: FilterCallable) -> None:
        """Add a global filter for all messages.

        Args:
            filter: The filter to add.

        Example:
            >>> manager.add_filter(allowed_chats([1234567890]))
        """
        self._filters.append(filter)

    def schedule(self, cron: str, task: ScheduleCallable) -> None:
        """Add a schedule task to run periodically.

        Args:
            cron: The cron expression.
            task: The task to add.

        Example:
            >>> manager.schedule("*/5 * * * *", task)
        """
        self._schedules.append(Schedule(cron, task))

    def start(self) -> None:
        """Start the bot to run the updates and scheduled tasks."""
        asyncio.run(self.astart())

    async def astart(self) -> None:
        """Start the bot to run the updates and scheduled tasks."""
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._run_updates())
            tg.create_task(self._run_scheduler())

    async def _run_updates(self) -> None:
        while True:
            for update in await self.bot.get_updates(self.poll_interval, self.allowed_updates):
                context = Context(self.bot, update)
                if await self._filter_context(context):
                    await self._handle_update(context)

    async def _filter_context(self, ctx: Context) -> bool:
        for filter in self._filters:
            if not await filter(ctx):
                return False
        return True

    async def _handle_update(self, ctx: Context) -> None:
        if ctx.text is not None and ctx.is_command:
            alias = ctx.text.split(" ")[0]
            if (command := self._commands.get(alias)) is not None:
                await command(ctx)
        elif ctx.is_text_message:
            for handler in self._text_handlers:
                await handler(ctx)

    async def _run_scheduler(self) -> None:
        async with asyncio.TaskGroup() as tg:
            for schedule in self._schedules:
                tg.create_task(self._run_schedule(schedule))

    async def _run_schedule(self, schedule: Schedule) -> None:
        for next_run in croniter(schedule.cron, datetime.now()).all_next(datetime):
            logger.info("Scheduled task '{}' will start at {}.", schedule.task.__name__, next_run)
            await sleep_until(next_run)

            logger.info("Starting scheduled task '{}'.", schedule.task.__name__)
            await schedule.task(self.bot)
            logger.info("Finished scheduled task '{}'.", schedule.task.__name__)
