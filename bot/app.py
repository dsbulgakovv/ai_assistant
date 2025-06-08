import os
import sys
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from redis.asyncio import Redis

from handlers import setup_handlers


logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)

TOKEN = os.getenv('BOT_TOKEN')
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST", "postgres")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
# DATABASE_URL = (
#     f'postgres://{db_user}:{db_pass}@'
#     f'{db_host}/{os.getenv("DB_NAME")}'
# )

redis_connection = Redis(host='redis', port=5370, db=0)
storage = RedisStorage(redis=redis_connection, key_builder=DefaultKeyBuilder(with_destiny=True))
job_store = {'default': SQLAlchemyJobStore(url=DATABASE_URL)}

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
scheduler = AsyncIOScheduler(jobstores=job_store, timezone='Europe/Moscow')
dp = Dispatcher(storage=storage)


async def set_commands(bot: Bot):
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='help', description='Справка')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def main() -> None:
    setup_handlers(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    await dp.start_polling(bot)
    await scheduler.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
