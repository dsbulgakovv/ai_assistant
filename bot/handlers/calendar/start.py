import datetime
import logging
import os

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from keyboards.calendar import (
    start_calendar_keyboard,
    start_manual_calendar_keyboard,
    task_name_manual_calendar_keyboard,
    task_category_manual_calendar_keyboard,
    task_description_manual_calendar_keyboard,
    task_start_dtm_manual_calendar_keyboard,
    task_duration_manual_calendar_keyboard,
    task_approval_manual_calendar_keyboard
)
from utils.database_api import DatabaseAPI


logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)

router = Router()
api = DatabaseAPI()


class StartCalendar(StatesGroup):
    start_calendar = State()
    start_manual_calendar = State()


@router.message(F.text.casefold() == 'мой календарь')
async def start_calendar_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Запиши мне голосовое сообщение или напиши текст, чтобы\n"
        "- добавить новое событие\n"
        "- увидеть предстоящие события\n"
        "- удалить/изменить предстоящие события\n"
        "или перейди в мануальный режим",
        reply_markup=start_calendar_keyboard()
    )
    await state.set_state(StartCalendar.start_calendar)


@router.message(StateFilter(StartCalendar.start_calendar), F.text.casefold() == 'мануальный режим')
async def start_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Теперь ты в мануальном режиме.\n"
        "Выбери нужное действие",
        reply_markup=start_manual_calendar_keyboard()
    )
    await state.set_state(StartCalendar.start_manual_calendar)


def setup_calendar_start_handlers(dp):
    dp.include_router(router)
