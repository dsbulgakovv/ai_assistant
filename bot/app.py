import sys
import asyncio
import logging

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

from core import bot, dp, scheduler

from handlers import setup_handlers


logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)


async def set_commands(bot: Bot):
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='help', description='Справка')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def main() -> None:
    setup_handlers(dp)
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
