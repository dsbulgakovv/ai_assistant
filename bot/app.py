import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
# from aiogram.utils.markdown import hbold
# from handlers import recommend, user_info
# from handlers.user_info import User
# from keyboards.data import share_data_keyboard
# from keyboards.general import start_keyboard
# from utils.db import check_user


TOKEN = '6675850647:AAGMrJUk2t4CV2oHwtz7QNxrR0vPn30Bbac'

dp = Dispatcher()
dp["user_data"] = {}

router = Router()

logger = logging.getLogger('aiogram')
# logger.info(f'path: {os.getcwd()}')


class Abilities(StatesGroup):
    voice_to_text = State()


@dp.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        "Я виртуальный ассистент.\nВыбери нужное действие."
    )
    await state.set_state(None)


@dp.message(Command('help'))
async def command_start_handler(message: types.Message) -> None:
    await message.answer(
        "Бот умеет:\n"
        "- расшифровывать аудио сообщение /voice_to_text"
    )


@dp.message(Command('voice_to_text'))
async def command_start_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Запиши мне голосовое сообщение и я пришлю его расшифровку."
    )
    await state.set_state(Abilities.voice_to_text)


@dp.message(StateFilter(Abilities.voice_to_text))
async def voice_transcriptor(message: types.Message, bot: Bot, state: FSMContext) -> None:
    if message.voice:
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_name = f"files/audio_{file_id}.mp3"
        await bot.download_file(file_path, file_name)
        await message.answer('Голосовое сообщение сохранено!')
    else:
        await message.answer('Пришли голсоовое сообщение')


@dp.message(StateFilter(None))
async def voice_transcriptor(message: types.Message) -> None:
    await message.answer(f"Выбери нужную функцию!")


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
