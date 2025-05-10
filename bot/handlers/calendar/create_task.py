import datetime
import logging
import os

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from .start import (
    start_manual_calendar_handler,
    StartCalendar
)

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


class CreateEvent(StatesGroup):
    waiting_task_name = State()
    waiting_task_category = State()
    waiting_task_description = State()
    waiting_task_start_dtm = State()
    waiting_task_end_dtm = State()
    waiting_approval = State()


@router.message(StateFilter(StartCalendar.start_manual_calendar), F.text.casefold() == 'создать новое событие')
async def create_event_task_name_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Введи название события",
        reply_markup=task_name_manual_calendar_keyboard()
    )
    await state.set_state(CreateEvent.waiting_task_name)


@router.message(StateFilter(CreateEvent.waiting_task_name))
async def create_event_task_category_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    if message.text.lower() == 'отмена':
        await state.set_state(StartCalendar.get_back_to_manual)
        await message.answer("Возвращаемся...")
    else:
        if not message.text or message.text.strip() == "":
            await message.answer("Название не может быть пустым!")
            await state.set_state(CreateEvent.waiting_task_name)
            return
        else:
            if message.text.lower() == 'стандартное название':
                await state.update_data(task_name='Новое событие')
            else:
                await state.update_data(task_name=message.text)
            await message.answer(
                "Выбери категорию события",
                reply_markup=task_category_manual_calendar_keyboard()
            )
            await state.set_state(CreateEvent.waiting_task_category)


@router.message(StateFilter(CreateEvent.waiting_task_category))
async def create_event_task_description_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    if message.text.lower() == 'отмена':
        await state.set_state(StartCalendar.get_back_to_manual)
        await message.answer("Возвращаемся...")
    else:
        await message.answer(
            "Введи описание события",
            reply_markup=task_description_manual_calendar_keyboard()
        )
        await state.set_state(CreateEvent.waiting_task_description)


@router.message(StateFilter(CreateEvent.waiting_task_description))
async def create_event_task_start_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    if message.text.lower() == 'отмена':
        await state.set_state(StartCalendar.get_back_to_manual)
        await message.answer("Возвращаемся...")
    else:
        keyboards = task_start_dtm_manual_calendar_keyboard()
        await message.answer(
            "Выбери дату и время начала события",
            reply_markup=keyboards['reply']
        )
        today_dt = datetime.date.today()
        await message.answer(
            f"Выбранная дата: {str(today_dt)}",
            reply_markup=keyboards['inline']
        )
        await state.set_state(CreateEvent.waiting_task_start_dtm)


@router.message(StateFilter(CreateEvent.waiting_task_start_dtm), F.text.casefold() == 'дальше')
async def create_event_task_end_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    if message.text.lower() == 'отмена':
        await state.set_state(StartCalendar.get_back_to_manual)
        await message.answer("Возвращаемся...")
    else:
        keyboards = task_duration_manual_calendar_keyboard()
        await message.answer(
            "Выбери продолжительность события",
            reply_markup=keyboards['reply']
        )
        cur_dur = '15 мин'
        await message.answer(
            f"Выбранная продолжительность: {cur_dur}",
            reply_markup=keyboards['inline']
        )
        await state.set_state(CreateEvent.waiting_task_end_dtm)


@router.message(StateFilter(CreateEvent.waiting_task_end_dtm), F.text.casefold() == 'дальше')
async def create_event_task_approval_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    if message.text.lower() == 'отмена':
        await state.set_state(StartCalendar.get_back_to_manual)
        await message.answer("Возвращаемся...")
    else:
        await message.answer(
            "ВСЕ СОБЫТИЕ",
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            "Все верно?",
            reply_markup=task_approval_manual_calendar_keyboard()
        )

        await state.set_state(CreateEvent.waiting_approval)


@router.message(StateFilter(CreateEvent.waiting_approval), F.text.casefold() == 'подтвердить')
async def create_event_task_success_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "✅ Событие успешно создано!",
        reply_markup=start_manual_calendar_keyboard()
    )
    await state.set_state(StartCalendar.start_manual_calendar)


# @router.callback_query()
# async def callback_handler(callback: CallbackQuery, state: FSMContext, project_data: dict):
#     if callback.data == "main_menu":
#         await show_menu(callback.message, state)
#     elif callback.data == "about_us":
#         await cmd_info(callback.message, state)
#     elif callback.data == "show_gallery":
#         await show_gallery(callback.message, state)
#     elif callback.data == "show_more":
#         await state.set_state(InitStates.show_more_gallery)
#         await show_more_gallery(callback.message, state)
#     elif callback.data == "get_estimation":
#         await get_estimation(callback.message, state)
#     elif callback.data == "change_data":
#         await state.set_state(EstimationStates.square_metres)
#         await get_square_metres(callback.message, state)
#     elif callback.data == "all_right_data":
#         await show_price(callback.message, state, project_data)


def setup_calendar_create_task_handlers(dp):
    dp.include_router(router)
