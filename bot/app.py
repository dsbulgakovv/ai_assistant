import asyncio
import logging
import os
import sys

from datetime import date

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
from handlers import voice_to_text, q_and_a
from utils.database_api import DatabaseAPI
from texts import instructions


TOKEN = os.getenv('BOT_TOKEN')

# Подключаем Redis
redis_connection = Redis(host='redis', port=5370, db=0)
storage = RedisStorage(redis=redis_connection)

dp = Dispatcher(storage=storage)

db_api = DatabaseAPI()

router = Router()

logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)


class InitStates(StatesGroup):
    started = State()


@dp.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext) -> None:
    await state.set_state(InitStates.started)
    resp = await db_api.get_user(message.from_user.tg_user_id)
    if resp.status_code == 404:
        post_resp = await db_api.create_user(
            message.from_user.tg_user_id,
            message.from_user.username,
            message.from_user.full_name
        )
        if post_resp.status_code == 201:
            await message.answer(
                f"Привет, {message.from_user.full_name}!\n"
                "Профиль создан. Теперь ты можешь ознакомиться с функционалом и начать пользоваться."
            )
            await message.answer(
                instructions.start_instruction
            )
            await message.answer(
                f"Я виртуальный секретарь.\n"
                "Выбери нужное действие.",
                reply_markup=start_keyboard()
            )
    elif resp.status_code == 200:
        await message.answer(
            f"Привет, {message.from_user.full_name}!\n"
            "Виртуальный секретарь на связи.\n"
            "Выбери нужное действие.",
            reply_markup=start_keyboard()
        )
    else:
        await message.answer(
            f"INTERNAL SERVER ERROR.\n"
            f"Please, contact support https://t.me/dm1trybu",
            reply_markup=start_keyboard()
        )


@dp.message(Command('help'))
async def command_help_handler(message: types.Message, state: FSMContext) -> None:
    msg = (
        instructions.start_instruction
    )
    await message.answer(msg)
    await state.set_state(None)


@dp.message(F.text.casefold() == 'хватит')
async def process_end_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer('Закончили', reply_markup=ReplyKeyboardRemove())
    await state.clear()


@dp.message(StateFilter(None), ~(F.text.casefold() == 'расшифровка голоса'), ~(F.text.casefold() == 'задать вопрос'))
async def uncertainty_handler(message: types.Message) -> None:
    await message.answer(f"Выбери нужную функцию!")


async def set_commands(bot: Bot):
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='help', description='Справка')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def main() -> None:
    dp.include_routers(voice_to_text.router, q_and_a.router)
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
