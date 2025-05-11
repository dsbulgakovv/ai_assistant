import os
import sys
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from redis.asyncio import Redis

from handlers import setup_handlers


TOKEN = os.getenv('BOT_TOKEN')

redis_connection = Redis(host='redis', port=5370, db=0)
storage = RedisStorage(redis=redis_connection, key_builder=DefaultKeyBuilder(with_destiny=True))

logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)


async def set_commands(bot: Bot):
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='help', description='Справка')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher(storage=storage)
    setup_handlers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
