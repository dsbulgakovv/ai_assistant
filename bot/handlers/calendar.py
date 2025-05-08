import logging
import os

from aiogram import Bot, F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from keyboards.general import start_keyboard, end_keyboard
from utils.database_api import DatabaseAPI


logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)

router = Router()
api = DatabaseAPI()


class Calendar(StatesGroup):
    start_calendar = State()


@router.message(F.text.casefold() == 'мой календарь')
async def start_calendar_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Запиши мне голосовое сообщение с нужной задачей или перейди в мануальный режим.",
        reply_markup=end_keyboard()
    )
    await state.set_state(Calendar.start_calendar)


@router.message(StateFilter(None))
async def uncertainty_handler(message: types.Message) -> None:
    await message.answer(
        "Такой опции нет.\n"
        "Выбери нужную функцию"
    )
