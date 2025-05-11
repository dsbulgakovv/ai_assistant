import logging
from datetime import date
from typing import Any

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Calendar, Button, Select
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import CallbackQuery

logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)


router = Router()


class CalendarState(StatesGroup):
    select_date = State()
    select_hours = State()
    select_minutes = State()

#
# async def process_selected_date(
#         callback: CallbackQuery,
#         widget,
#         manager: DialogManager,
#         selected_date: date
# ):
#     await callback.answer(f"Вы выбрали: {selected_date}")
#
#     # Получаем FSMContext из данных менеджера
#     state: FSMContext = manager.middleware_data["state"]
#     await state.update_data(selected_date=str(selected_date))
#
#     await manager.done()  # Закрываем диалог
#
#     # Отправляем сообщение через оригинальный callback
#     await callback.message.answer(f"Выбранная дата: {selected_date}")


async def on_date_selected(
        callback: CallbackQuery,
        widget: Any,
        manager: DialogManager,
        selected_date: date
):
    state: FSMContext = manager.middleware_data["state"]
    await callback.answer()
    await state.update_data(selected_date=str(selected_date))
    await manager.switch_to(CalendarState.select_hours)


async def on_hour_selected(
        callback: CallbackQuery,
        widget: Any,
        manager: DialogManager,
        hour: str
):
    state: FSMContext = manager.middleware_data["state"]
    await state.update_data(hours=hour)
    await manager.switch_to(CalendarState.select_minutes)


async def on_minute_selected(
        callback: CallbackQuery,
        widget: Any,
        manager: DialogManager,
        minute: str
):
    state: FSMContext = manager.middleware_data["state"]
    data = await state.get_data()
    selected_date = data['selected_date']
    selected_time = f"{data['hours']}:{minute}"
    full_datetime = f"{selected_date} {selected_time}"

    state: FSMContext = manager.middleware_data["state"]
    await state.update_data(
        event_datetime=full_datetime,
        selected_time=selected_time
    )

    await manager.done()
    await callback.message.answer(f"Выбрано: {full_datetime}")


HOURS = [f"{h:02d}" for h in range(24)]
MINUTES = [f"{m:02d}" for m in range(0, 60, 5)]


calendar_dialog = Dialog(
    Window(
        Const("📅 Выберите дату события:"),
        Calendar(id="calendar", on_click=on_date_selected),
        state=CalendarState.select_date,
    ),
    Window(
        Const("🕒 Выберите час:"),
        Select(
            Format("{item}"),
            id="hours",
            items=HOURS,
            on_click=on_hour_selected
        ),
        state=CalendarState.select_hours,
    ),
    Window(
        Const("⏰ Выберите минуты:"),
        Select(
            Format("{item}"),
            id="minutes",
            items=MINUTES,
            on_click=on_minute_selected
        ),
        state=CalendarState.select_minutes,
    )
)


# calendar_dialog = Dialog(
#     Window(
#         Const("Календарь"),
#         Calendar(id="calendar", on_click=process_selected_date),
#         state=CalendarState.select_date,
#     )
# )


# Регистрируем диалог в роутере
router.include_router(calendar_dialog)


def setup_calendar_dialogue_select_date_handlers(dp):
    from aiogram_dialog import setup_dialogs
    dp.include_router(router)
    setup_dialogs(dp)
