import logging
from datetime import date

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Calendar
from aiogram_dialog.widgets.text import Const
from aiogram.types import CallbackQuery

logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)


router = Router()


class CalendarState(StatesGroup):
    select_date = State()


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


calendar_dialog = Dialog(
    Window(
        Const("Календарь"),
        Calendar(id="calendar", on_click=process_selected_date),
        state=CalendarState.select_date,
    )
)

# Регистрируем диалог в роутере
router.include_router(calendar_dialog)


def setup_calendar_dialogue_select_date_handlers(dp):
    from aiogram_dialog import setup_dialogs
    dp.include_router(router)
    setup_dialogs(dp)
