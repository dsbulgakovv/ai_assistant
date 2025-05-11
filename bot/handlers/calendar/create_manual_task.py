from datetime import datetime, timedelta
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
    waiting_task_end_dt = State()
    waiting_approval = State()


def get_rounded_datetime():
    now = datetime.now()

    # Округляем до ближайших 30 минут
    minute = now.minute
    if minute < 15:
        # Округляем вниз до полного часа
        rounded = now.replace(minute=0, second=0, microsecond=0)
    elif 15 <= minute < 45:
        # Округляем до 30 минут
        rounded = now.replace(minute=30, second=0, microsecond=0)
    else:
        # Округляем вверх до следующего часа
        rounded = (now.replace(minute=0, second=0, microsecond=0)
                   + timedelta(hours=1))

    next_rounded = rounded + timedelta(minutes=30)

    # Форматируем в строку дд.мм.гггг чч:мм
    formatted_cur = rounded.strftime("%d.%m.%Y %H:%M")
    formatted_next = next_rounded.strftime("%d.%m.%Y %H:%M")

    return formatted_cur, formatted_next


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
            if message.text.lower() == 'без названия':
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
            await state.update_data(task_description='...')
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

        start_nearest_dtm, end_nearest_dtm = get_rounded_datetime()
        await state.update_data(start_dtm=start_nearest_dtm)
        await state.update_data(end_dtm=end_nearest_dtm)
        await message.answer(
            f"Выбери дату и время начала события.\n"
            f"Нажми *Дальше*, чтобы выбрать ближайшую: {start_nearest_dtm}",
            reply_markup=task_start_dt_manual_calendar_keyboard()
        )
        await dialog_manager.start(
            CalendarState.select_date,
            mode=StartMode.RESET_STACK
        )
        await state.set_state(CreateEvent.waiting_task_start_dt)


@router.message(StateFilter(CreateEvent.waiting_task_start_dt))
async def create_event_task_end_manual_calendar_handler(
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
            "Добавим ссылку на встречу?",
            reply_markup=task_link_manual_calendar_keyboard()
        )
        await state.set_state(CreateEvent.waiting_task_link)
    elif message.text.lower() == 'дальше':
        data = await state.get_data()
        selected_datetime = data.get("event_datetime")
        if selected_datetime:
            await state.update_data(event_datetime=None)
            await state.update_data(start_dtm=selected_datetime)
            after_selected_datetime = (
                datetime.strptime(selected_datetime, "%d.%m.%Y %H:%M") + timedelta(minutes=30)
            ).strftime("%d.%m.%Y %H:%M")
            await state.update_data(end_dtm=after_selected_datetime)
        data = await state.get_data()
        end_nearest_dtm = data.get('end_dtm')
        await message.answer(
            "Выбери дату и время заверешния события.\n"
            f"Нажми *Дальше*, чтобы выбрать ближайшую: {end_nearest_dtm}",
            reply_markup=task_duration_manual_calendar_keyboard()
        )
        await dialog_manager.start(
            CalendarState.select_date,
            mode=StartMode.RESET_STACK
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
        start_nearest_dtm, end_nearest_dtm = get_rounded_datetime()
        await state.update_data(start_dtm=start_nearest_dtm)
        await state.update_data(end_dtm=end_nearest_dtm)
        await message.answer(
            f"Выбери дату и время начала события.\n"
            f"Нажми *Дальше*, чтобы выбрать ближайшую: {start_nearest_dtm}",
            reply_markup=task_start_dt_manual_calendar_keyboard()
        )
        await dialog_manager.start(
            CalendarState.select_date,
            mode=StartMode.RESET_STACK
        )
        await state.set_state(CreateEvent.waiting_task_start_dt)
    elif message.text.lower() == 'дальше':
        data = await state.get_data()
        selected_datetime = data.get("event_datetime")
        if selected_datetime:
            await state.update_data(event_datetime=None)
            await state.update_data(end_dtm=selected_datetime)

        data = await state.get_data()
        await message.answer(
            calendar.event_desc.format(
                data.get('task_name'),
                data.get('start_dtm'),
                data.get('end_dtm'),
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
async def create_event_task_success_manual_calendar_handler(
        message: types.Message, state: FSMContext, dialog_manager: DialogManager) -> None:
    if message.text.lower() == 'отмена':
        await message.answer(
            "Выбери нужное действие",
            reply_markup=start_manual_calendar_keyboard()
        )
        await state.clear()
        await state.set_state(StartCalendar.start_manual_calendar)
    elif message.text.lower() == 'к предыдущему шагу':
        data = await state.get_data()
        end_nearest_dtm = data.get('end_dtm')
        await message.answer(
            "Выбери дату и время заверешния события.\n"
            f"Нажми *Дальше*, чтобы выбрать ближайшую: {end_nearest_dtm}",
            reply_markup=task_duration_manual_calendar_keyboard()
        )
        await dialog_manager.start(
            CalendarState.select_date,
            mode=StartMode.RESET_STACK
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


def setup_calendar_create_task_handlers(dp):
    dp.include_router(router)
