import asyncio
import os

import httpx

from lite_telegram import TelegramBot, BotManager, Context, allowed_chats


TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


async def command_hello(context: Context) -> None:
    await context.reply("hello")

async def every_min(bot: TelegramBot):
    await bot.send_message(TELEGRAM_CHAT_ID, "schedule every min!")


async def main():
    async with httpx.AsyncClient() as aclient:
        bot = TelegramBot(aclient, TELEGRAM_TOKEN)

        # await bot.send_message(TELEGRAM_CHAT_ID, "hi")


        manager = BotManager(bot, allowed_updates=["message"])
        manager.add_filter(allowed_chats(TELEGRAM_CHAT_ID))
        manager.add_command("/hello", command_hello)
        manager.schedule("* * * * *", every_min)
        await manager.astart()


if __name__ == "__main__":
    asyncio.run(main())
