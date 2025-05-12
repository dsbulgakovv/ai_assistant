import pytz
import logging
from datetime import datetime, timedelta, timezone

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import StartMode

from .start import StartCalendar

from .calendar_util import CalendarState
from texts.calendar import build_event_full_info
from keyboards.calendar import (
    start_manual_calendar_keyboard,
    only_back_to_manual_calendar_menu_keyboard,
    swiping_tasks_with_nums_inline_keyboard,
    swiping_tasks_no_nums_inline_keyboard,
    change_delete_task_inline_keyboard
)
from utils.database_api import DatabaseAPI

logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)

router = Router()
db_api = DatabaseAPI()


class ShowEvent(StatesGroup):
    waiting_events_show_end = State()


@router.message(StateFilter(StartCalendar.start_manual_calendar), F.text.casefold() == 'посмотреть предстоящие события')
async def show_nearest_events_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Введи название события",
        reply_markup=only_back_to_manual_calendar_menu()
    )
    await state.set_state(ShowEvent.waiting_events_show_end)


@router.message(StateFilter(ShowEvent.waiting_events_show_end), F.text.casefold() == 'вернуться в меню')
async def close_show_nearest_events_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Выбери нужное действие",
        reply_markup=start_manual_calendar_keyboard()
    )
    await state.clear()
    await state.set_state(StartCalendar.start_manual_calendar)












async def show_events(message: types.Message, state: FSMContext, day_offset=0):
    # Получаем текущую дату с учетом смещения
    current_date = datetime.now() + timedelta(days=day_offset)
    date_str = current_date.strftime("%Y-%m-%d")

    # Здесь получаем события из вашего API/Redis
    events = await get_events_for_date(message.from_user.id, date_str)

    # Сохраняем текущую дату и события в FSM
    await state.update_data(
        current_date=date_str,
        events=events,
        day_offset=day_offset
    )

    if not events:
        # Если событий нет
        left_right_inline_no_nums_kb = swiping_tasks_no_nums_inline_keyboard(day_offset)
        await message.answer(f"На {date_str} событий нет.", reply_markup=left_right_inline_no_nums_kb)
        await state.set_state(ShowEvent.waiting_events_show_end)
        return

    # Формируем текст сообщения
    text = f"События на {date_str}:\n\n"
    for i, event in enumerate(events, 1):
        text += f"{i}. {event['title']} ({event['time']})\n"

    left_right_inline_with_nums_kb = swiping_tasks_with_nums_inline_keyboard(events, day_offset)

    # Если у нас уже есть message_id в состоянии, редактируем сообщение
    data = await state.get_data()
    if 'events_message_id' in data:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=data['events_message_id'],
                text=text,
                reply_markup=left_right_inline_with_nums_kb
            )
            await state.set_state(ShowEvent.waiting_events_show_end)
            return
        except Exception as e:
            logger.debug(e)
            pass

    # Иначе отправляем новое сообщение
    msg = await message.answer(text, reply_markup=left_right_inline_with_nums_kb)

    # Сохраняем ID сообщения в состоянии
    await state.update_data(events_message_id=msg.message_id)
    await state.set_state(ShowEvent.waiting_events_show_end)


@router.callback_query(F.data.startswith(('prev_day_', 'next_day_')), StateFilter(ShowEvent.waiting_events_show_end))
async def handle_day_navigation(callback: types.CallbackQuery, state: FSMContext):
    # Получаем направление и текущее смещение
    direction = callback.data.split('_')[0]
    current_offset = int(callback.data.split('_')[-1])

    # Вычисляем новое смещение
    new_offset = current_offset - 1 if direction == "prev" else current_offset + 1

    # "Переотправляем" сообщение с новым смещением
    await show_events(callback.message, state, new_offset)
    await callback.answer()


@router.callback_query(F.data.startswith('event_'), StateFilter(ShowEvent.waiting_events_show_end))
async def show_event_details(callback: types.CallbackQuery, state: FSMContext):
    # Получаем номер события из callback_data
    event_num = int(callback.data.split('_')[1])

    data = await state.get_data()
    events = data['events']
    day_offset = data['day_offset']

    if event_num < 1 or event_num > len(events):
        await callback.answer("Неверный номер события")
        return

    event = events[event_num - 1]

    # Формируем текст с полным описанием
    text = f"Событие {event_num}:\n\n"
    text += f"📌 {event['title']}\n"
    text += f"🕒 {event['time']}\n"
    text += f"📅 {event['date']}\n"
    text += f"📝 {event['description']}\n"

    # Создаем клавиатуру с действиями
    delete_change_inline_kb = change_delete_task_inline_keyboard(day_offset)

    # Редактируем сообщение
    await callback.message.edit_text(text, reply_markup=delete_change_inline_kb)
    await callback.answer()


@router.callback_query(F.data.startswith('back_to_list_'), StateFilter(ShowEvent.waiting_events_show_end))
async def back_to_events_list(callback: types.CallbackQuery, state: FSMContext):
    # Получаем смещение из callback_data
    day_offset = int(callback.data.split('_')[-1])

    # Возвращаемся к списку событий
    await show_events(callback.message, state, day_offset)
    await callback.answer()


@router.message(StateFilter(ShowEvent.waiting_events_show), F.text.casefold() == "мои события на сегодня")
async def handle_show_events(message: types.Message, state: FSMContext):
    await show_events(message, state)


@router.message(StateFilter(ShowEvent.waiting_events_show_end), F.text.casefold() == "вернуться в меню")
async def return_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    # Здесь добавьте ваш код для возврата в главное меню
    await message.answer("Вы вернулись в главное меню", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Мои события на сегодня")]],
        resize_keyboard=True
    ))


# Пример функции для получения событий (замените на свою реализацию)
async def get_events_for_date(user_id: int, date_str: str):
    # Здесь должна быть ваша реализация получения событий из Redis/API
    # Возвращаем список словарей с событиями
    return [
        {
            "title": "Встреча с клиентом",
            "time": "10:00",
            "date": date_str,
            "description": "Обсуждение нового проекта"
        },
        {
            "title": "Обед",
            "time": "13:00",
            "date": date_str,
            "description": "Кафе на углу"
        }
    ]











def setup_calendar_show_tasks_handlers(dp):
    dp.include_router(router)
