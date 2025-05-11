import logging
from datetime import date
from typing import Any

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Calendar, NumberKeyboard, Button
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import CallbackQuery

logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)


router = Router()


class CalendarState(StatesGroup):
    select_date = State()
    select_time = State()


async def process_selected_date(
        callback: CallbackQuery,
        widget,
        manager: DialogManager,
        selected_date: date
):
    await callback.answer(f"Вы выбрали: {selected_date}")

    # Получаем FSMContext из данных менеджера
    state: FSMContext = manager.middleware_data["state"]
    await state.update_data(selected_date=str(selected_date))

    await manager.done()  # Закрываем диалог

    # Отправляем сообщение через оригинальный callback
    await callback.message.answer(f"Выбранная дата: {selected_date}")


async def on_date_selected(
        callback: CallbackQuery,
        widget: Any,
        manager: DialogManager,
        selected_date: date
):
    await callback.answer()
    await manager.update_data(selected_date=str(selected_date))
    await manager.switch_to(CalendarState.select_time)


async def on_time_changed(
        event: Any,
        widget: Any,
        manager: DialogManager,
        value: int
):
    widget_id = widget.widget_id
    manager.dialog_data[widget_id] = f"{value:02d}"


async def on_time_confirmed(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    data = manager.dialog_data
    hours = data.get("hours", "00")
    minutes = data.get("minutes", "00")
    selected_time = f"{hours}:{minutes}"

    # Получаем выбранную дату
    selected_date = data.get("selected_date")
    full_datetime = f"{selected_date} {selected_time}"

    # Сохраняем в FSMContext
    state: FSMContext = manager.middleware_data["state"]
    await state.update_data(
        event_datetime=full_datetime,
        selected_time=selected_time
    )

    await manager.done()
    await callback.message.answer(f"✅ Выбрано: {full_datetime}")


calendar_dialog = Dialog(
    Window(
        Const("📅 Выберите дату события:"),
        Calendar(id="calendar", on_click=on_date_selected),
        state=CalendarState.select_date,
    ),
    Window(
        Const("⏰ Установите время:"),
        NumberKeyboard(
            id="hours",
            on_value_changed=on_time_changed,
            max_value=23
        ),
        Const(":"),
        NumberKeyboard(
            id="minutes",
            on_value_changed=on_time_changed,
            max_value=59
        ),
        Button(
            Const("✅ Подтвердить время"),
            id="confirm_time",
            on_click=on_time_confirmed
        ),
        state=CalendarState.select_time,
        getter=lambda dialog_manager: {
            "hours": dialog_manager.dialog_data.get("hours", "12"),
            "minutes": dialog_manager.dialog_data.get("minutes", "00")
        }
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
