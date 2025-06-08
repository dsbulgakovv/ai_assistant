import datetime
import logging
import os

from aiogram import F, Router, types
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from keyboards.calendar import (
    start_calendar_keyboard,
    start_manual_calendar_keyboard,
)
from utils.database_api import DatabaseAPI


logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)

router = Router()
api = DatabaseAPI()


class StartCalendar(StatesGroup):
    start_calendar = State()
    start_manual_calendar = State()


class ShowVoiceEvents(StatesGroup):
    waiting_events_show_end = State()


@router.message(F.text.casefold() == 'мой календарь')
async def start_calendar_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Запиши голосовое сообщение 🎙️, чтобы:\n"
        "➕ Добавить новое событие\n"
        "👀 Просмотреть предстоящие встречи\n"
        "✏️ Изменить или удалить существующие события\n"
        "Перейди в ✋ мануальный режим для управления кнопками.",
        reply_markup=start_calendar_keyboard()
    )
    await state.clear()
    await state.set_state(StartCalendar.start_calendar)


@router.message(
    or_f(
        StateFilter(StartCalendar.start_calendar),
        StateFilter(ShowVoiceEvents.waiting_events_show_end)
    ),
    F.text.casefold() == 'мануальный режим'
)
async def start_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Теперь ты в мануальном режиме.\n"
        "Выбери нужное действие",
        reply_markup=start_manual_calendar_keyboard()
    )
    await state.set_state(StartCalendar.start_manual_calendar)


def setup_calendar_start_handlers(dp):
    dp.include_router(router)
