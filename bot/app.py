import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BotCommand, BotCommandScopeDefault, ReplyKeyboardRemove

from keyboards.general import start_keyboard, end_keyboard

from utils.voice_to_text_api import VoiceToTextAPI

# from aiogram.utils.markdown import hbold
# from handlers import recommend, user_info
# from handlers.user_info import User
# from keyboards.data import share_data_keyboard
# from keyboards.general import start_keyboard
# from utils.db import check_user
# import speech_recognition as sr
# import subprocess


# def convert_voice_to_text(path_to_file: str):
#     path_to_wav_file = path_to_file[:-3] + 'wav'
#     subprocess.call(['ffmpeg', '-i', path_to_file, path_to_wav_file])
#
#     # Распознаем речь из аудио файла
#     with sr.AudioFile(path_to_wav_file) as source:
#         recognizer = sr.Recognizer()
#         audio_data = recognizer.record(source)
#         text = recognizer.recognize_google(audio_data, language="ru")
#
#     return text, path_to_wav_file


TOKEN = '6675850647:AAGMrJUk2t4CV2oHwtz7QNxrR0vPn30Bbac'

dp = Dispatcher(storage=MemoryStorage())
dp["user_data"] = {}

router = Router()

logger = logging.getLogger('aiogram')

api = VoiceToTextAPI()


class Abilities(StatesGroup):
    voice_to_text = State()


@dp.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        "Я виртуальный ассистент.\nВыбери нужное действие.",
        reply_markup=start_keyboard()
    )
    await state.set_state(None)


@dp.message(Command('help'))
async def command_help_handler(message: types.Message) -> None:
    msg = (
        "Бот умеет:\n"
        "- расшифровывать аудио сообщение\n"
        "- что-то еще"
    )
    await message.answer(msg)


@dp.message(F.text.casefold() == 'расшифровка голоса')
async def voice_to_text_start_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Запиши мне голосовое сообщение и я пришлю его расшифровку.",
        reply_markup=end_keyboard()
    )
    await state.set_state(Abilities.voice_to_text)


@dp.message(StateFilter(Abilities.voice_to_text))
async def voice_to_text_process_handler(message: types.Message, bot: Bot, state: FSMContext) -> None:
    if message.voice:
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_name = f"files/audio_{file_id}.mp3"
        await bot.download_file(file_path, file_name)
        await message.answer('Голосовое сообщение обработано!', reply_markup=end_keyboard())
        text, path_to_wav_file = convert_voice_to_text(file_name)
        await message.answer(text, reply_markup=end_keyboard())
        os.remove(file_name)
        os.remove(path_to_wav_file)
    else:
        if message.text == 'Хватит':
            await message.answer('Закончили', reply_markup=ReplyKeyboardRemove())
            await state.clear()
        else:
            await message.answer('Пришли голсоовое сообщение', reply_markup=end_keyboard())


@dp.message(F.text.casefold() == 'хватит')
async def process_end_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer('Закончили', reply_markup=ReplyKeyboardRemove())
    await state.clear()


@dp.message(StateFilter(None))
async def uncertainty_handler(message: types.Message) -> None:
    await message.answer(f"Выбери нужную функцию!")


async def set_commands(bot: Bot):
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='help', description='Справка')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
