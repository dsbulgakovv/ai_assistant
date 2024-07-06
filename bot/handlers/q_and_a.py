import logging
import os

from aiogram import Bot, F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from keyboards.general import start_keyboard, end_keyboard
from utils.voice_to_text_api import VoiceToTextAPI


logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)

markup_text = "<b>Текст:</b>\n{}"

router = Router()
api = VoiceToTextAPI()


# @router.message(StateFilter(None))
# async def uncertainty_handler(message: types.Message) -> None:
#     await message.answer(f"Выбери нужную функцию!")
