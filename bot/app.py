import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BotCommand, BotCommandScopeDefault, ReplyKeyboardRemove
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from redis.asyncio import Redis

from keyboards.general import start_keyboard
from handlers import setup_handlers
from utils.database_api import DatabaseAPI
from texts import instructions


TOKEN = os.getenv('BOT_TOKEN')

redis_connection = Redis(host='redis', port=5370, db=0)
storage = RedisStorage(redis=redis_connection)

dp = Dispatcher(storage=storage)

db_api = DatabaseAPI()

logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)


async def set_commands(bot: Bot):
    commands = [BotCommand(command='start', description='Старт/Вернуться в меню'),
                BotCommand(command='help', description='Справка')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def main() -> None:
    dp.include_routers(voice_to_text.router, q_and_a.router, calendar.router)
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
