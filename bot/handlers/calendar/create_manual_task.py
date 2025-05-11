import datetime
import logging
import os

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import StartMode

from .start import StartCalendar

from .calendar_util import CalendarState
from texts import calendar
from keyboards.calendar import (
    start_calendar_keyboard,
    start_manual_calendar_keyboard,
    task_name_manual_calendar_keyboard,
    task_category_manual_calendar_keyboard,
    task_description_manual_calendar_keyboard,
    task_link_manual_calendar_keyboard,
    task_start_dt_manual_calendar_keyboard,
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
    waiting_task_link = State()
    waiting_task_start_dt = State()
    waiting_task_start_time = State()
    waiting_task_end_dt = State()
    waiting_task_end_time = State()
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
        await message.answer(
            "Выбери нужное действие",
            reply_markup=start_manual_calendar_keyboard()
        )
        await state.clear()
        await state.set_state(StartCalendar.start_manual_calendar)
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
        await message.answer(
            "Выбери нужное действие",
            reply_markup=start_manual_calendar_keyboard()
        )
        await state.clear()
        await state.set_state(StartCalendar.start_manual_calendar)
    elif message.text.lower() == 'к предыдущему шагу':
        await message.answer(
            "Введи название события заново",
            reply_markup=task_name_manual_calendar_keyboard()
        )
        await state.set_state(CreateEvent.waiting_task_name)
    else:
        if message.text not in ['Личное', 'Работа', 'Учеба', 'Семья', 'Здоровье', 'Финансы']:
            await message.answer(
                "Такой категории нет."
                "Выбери категорию события",
                reply_markup=task_category_manual_calendar_keyboard()
            )
            await state.set_state(CreateEvent.waiting_task_category)
        else:
            await state.update_data(task_category=message.text)
            await message.answer(
                "Введи описание события",
                reply_markup=task_description_manual_calendar_keyboard()
            )
            await state.set_state(CreateEvent.waiting_task_description)


@router.message(StateFilter(CreateEvent.waiting_task_description))
async def create_event_task_link_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    if message.text.lower() == 'отмена':
        await message.answer(
            "Выбери нужное действие",
            reply_markup=start_manual_calendar_keyboard()
        )
        await state.clear()
        await state.set_state(StartCalendar.start_manual_calendar)
    elif message.text.lower() == 'к предыдущему шагу':
        await message.answer(
            "Выбери категорию события заново",
            reply_markup=task_category_manual_calendar_keyboard()
        )
        await state.set_state(CreateEvent.waiting_task_category)
    else:
        if message.text.lower() == 'без описания':
            await state.update_data(task_description=None)
        else:
            await state.update_data(task_description=message.text)

        await message.answer(
            "Добавим ссылку на встречу?",
            reply_markup=task_link_manual_calendar_keyboard()
        )
        await state.set_state(CreateEvent.waiting_task_link)


@router.message(StateFilter(CreateEvent.waiting_task_link))
async def create_event_task_start_manual_calendar_handler(
        message: types.Message, state: FSMContext, dialog_manager: DialogManager) -> None:
    if message.text.lower() == 'отмена':
        await message.answer(
            "Выбери нужное действие",
            reply_markup=start_manual_calendar_keyboard()
        )
        await state.clear()
        await state.set_state(StartCalendar.start_manual_calendar)
    elif message.text.lower() == 'к предыдущему шагу':
        await message.answer(
            "Введи описание события заново",
            reply_markup=task_description_manual_calendar_keyboard()
        )
        await state.set_state(CreateEvent.waiting_task_description)
    else:
        if message.text.lower() == 'без ссылки':
            await state.update_data(task_link=None)
        else:
            await state.update_data(task_link=message.text)

        await message.answer(
            "Выбери дату начала события",
            reply_markup=task_start_dt_manual_calendar_keyboard()
        )
        await dialog_manager.start(
            CalendarState.select_date,
            mode=StartMode.RESET_STACK
        )
        await state.set_state(CreateEvent.waiting_task_start_dt)


@router.message(StateFilter(CreateEvent.waiting_task_start_dt))
async def create_event_task_end_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    if message.text.lower() == 'отмена':
        await message.answer(
            "Выбери нужное действие",
            reply_markup=start_manual_calendar_keyboard()
        )
        await state.clear()
        await state.set_state(StartCalendar.start_manual_calendar)
    elif message.text.lower() == 'к предыдущему шагу':
        await message.answer(
            "Добавим ссылку на встречу?",
            reply_markup=task_link_manual_calendar_keyboard()
        )
        await state.set_state(CreateEvent.waiting_task_link)
    elif message.text.lower() == 'дальше':
        keyboards = task_duration_manual_calendar_keyboard()
        await message.answer(
            "Выбери продолжительность события",
            reply_markup=keyboards['reply']
        )
        cur_dur = '15 мин'

        data = await state.get_data()
        selected_date = data.get("selected_date")
        await state.update_data(start_dt=selected_date)

        await state.update_data(task_duration=cur_dur)
        await state.update_data(end_dt=selected_date)
        await message.answer(
            f"Выбранная продолжительность: {cur_dur}",
            reply_markup=keyboards['inline']
        )
        await state.set_state(CreateEvent.waiting_task_end_dt)
    else:
        await message.answer("Не та команда")


@router.message(StateFilter(CreateEvent.waiting_task_end_dt))
async def create_event_task_approval_manual_calendar_handler(
        message: types.Message, state: FSMContext, dialog_manager: DialogManager) -> None:
    if message.text.lower() == 'отмена':
        await message.answer(
            "Выбери нужное действие",
            reply_markup=start_manual_calendar_keyboard()
        )
        await state.clear()
        await state.set_state(StartCalendar.start_manual_calendar)
    elif message.text.lower() == 'к предыдущему шагу':
        await message.answer(
            "Выбери дату начала события",
            reply_markup=task_start_dt_manual_calendar_keyboard()
        )
        await dialog_manager.start(
            CalendarState.select_date,
            mode=StartMode.RESET_STACK
        )
        await state.set_state(CreateEvent.waiting_task_start_dt)
    elif message.text.lower() == 'изменить дату завершения':
        await message.answer(
            "Выбери дату завершения события",
            reply_markup=task_start_dt_manual_calendar_keyboard()
        )
        await dialog_manager.start(
            CalendarState.select_date,
            mode=StartMode.RESET_STACK
        )
        await state.set_state(CreateEvent.waiting_task_end_dt)
    elif message.text.lower() == 'дальше':
        data = await state.get_data()
        selected_date = data.get("selected_date")
        data['end_dt'] = selected_date
        await state.update_data(end_dt=selected_date)

        if not data['task_description']:
            data['task_description'] = '...'
        await message.answer(
            calendar.event_desc.format(
                data.get('task_name'),
                data.get('start_dt'),
                data.get('end_dt'),
                data.get('task_duration'),
                data.get('task_category'),
                data.get('task_description')
            ),
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            "Все верно?",
            reply_markup=task_approval_manual_calendar_keyboard()
        )
        await state.set_state(CreateEvent.waiting_approval)
    else:
        await message.answer("Не та команда")


@router.message(StateFilter(CreateEvent.waiting_approval))
async def create_event_task_success_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    if message.text.lower() == 'отмена':
        await message.answer(
            "Выбери нужное действие",
            reply_markup=start_manual_calendar_keyboard()
        )
        await state.clear()
        await state.set_state(StartCalendar.start_manual_calendar)
    elif message.text.lower() == 'к предыдущему шагу':
        keyboards = task_duration_manual_calendar_keyboard()
        await message.answer(
            "Выбери продолжительность события",
            reply_markup=keyboards['reply']
        )
        cur_dur = '15 мин'
        await state.update_data(task_duration=cur_dur)
        await message.answer(
            f"Выбранная продолжительность: {cur_dur}",
            reply_markup=keyboards['inline']
        )
        await state.set_state(CreateEvent.waiting_task_end_dt)
    elif message.text.lower() == 'подтвердить':
        await message.answer(
            "✅ Событие успешно создано!",
            reply_markup=start_manual_calendar_keyboard()
        )
        await state.clear()
        await state.set_state(StartCalendar.start_manual_calendar)
    else:
        await message.answer("Не та команда")


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
