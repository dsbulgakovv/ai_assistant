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


def map_task_category(idx_category):
    categories_mapping = {
        1: 'Работа',
        2: 'Учеба',
        3: 'Личное',
        4: 'Здоровье',
        5: 'Финансы',
        6: 'Семья'
    }
    return categories_mapping[idx_category]


@router.message(StateFilter(StartCalendar.start_manual_calendar), F.text.casefold() == 'посмотреть предстоящие события')
async def show_nearest_events_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Ваши события",
        reply_markup=only_back_to_manual_calendar_menu_keyboard()
    )
    user_timezone = await db_api.get_user_timezone(message.from_user.id)
    if not user_timezone:
        user_timezone = "Europe/Moscow"
    await state.update_data(user_timezone=user_timezone, tg_user_id=message.from_user.id)
    await show_events(message, state)
    await state.set_state(ShowEvent.waiting_events_show_end)


@router.message(StateFilter(ShowEvent.waiting_events_show_end), F.text.casefold() == 'вернуться назад')
async def close_show_nearest_events_manual_calendar_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Выбери нужное действие",
        reply_markup=start_manual_calendar_keyboard()
    )
    await state.clear()
    await state.set_state(StartCalendar.start_manual_calendar)


async def show_events(message: types.Message, state: FSMContext):
    # Получаем текущую дату с учетом смещения
    data = await state.get_data()
    user_timezone = data['user_timezone']
    utc_time = datetime.now(timezone.utc)
    cur_date = utc_time.astimezone(pytz.timezone(user_timezone))

    if 'day_offset' in data:
        day_offset = data['day_offset']
    else:
        day_offset = 0
        await state.update_data(day_offset=day_offset)

    target_date_str = (cur_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")

    # Здесь получаем события из вашего API/Redis
    events, status = await db_api.get_tasks(data['tg_user_id'], target_date_str, target_date_str)
    await state.update_data(events=events)

    # Если событий нет
    if status == 404:
        left_right_inline_no_nums_kb = swiping_tasks_no_nums_inline_keyboard(day_offset)
        text = f"На {target_date_str} событий нет"
        if 'events_message_id' in data:
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=data['events_message_id'],
                    text=text,
                    reply_markup=left_right_inline_no_nums_kb
                )
            except Exception as e:
                logger.debug(e)
                pass
        else:
            msg = await message.answer(text, reply_markup=left_right_inline_no_nums_kb)
            await state.update_data(events_message_id=msg.message_id)
            await state.set_state(ShowEvent.waiting_events_show_end)

        await state.set_state(ShowEvent.waiting_events_show_end)
        return

    # Формируем текст сообщения
    text = f"События на <b>{target_date_str}</b>:\n\n"
    for cur_event in events:
        start_time = (
            datetime
            .fromisoformat(cur_event['task_start_dtm'])
            .astimezone(pytz.timezone(user_timezone))
            .time().strftime("%H:%M")
        )
        text += f"<b>{cur_event['task_relative_id']}.</b> <code>{start_time}</code> - {cur_event['task_name']}\n"

    left_right_inline_with_nums_kb = swiping_tasks_with_nums_inline_keyboard(events, day_offset)

    # Если у нас уже есть message_id в состоянии, редактируем сообщение
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

    # # Иначе отправляем новое сообщение
    msg = await message.answer(text, reply_markup=left_right_inline_with_nums_kb)

    # # Сохраняем ID сообщения в состоянии
    await state.update_data(events_message_id=msg.message_id)
    await state.set_state(ShowEvent.waiting_events_show_end)


@router.callback_query(F.data.startswith(('prev_day_', 'next_day_')), StateFilter(ShowEvent.waiting_events_show_end))
async def handle_day_navigation(callback: types.CallbackQuery, state: FSMContext):
    # Получаем направление и текущее смещение
    direction = callback.data.split('_')[0]
    # current_offset = int(callback.data.split('_')[-1])
    data = await state.get_data()
    current_offset = data['day_offset']

    # Вычисляем новое смещение
    new_offset = current_offset - 1 if direction == "prev" else current_offset + 1
    await state.update_data(day_offset=new_offset)

    # "Переотправляем" сообщение с новым смещением
    await show_events(callback.message, state)
    await callback.answer()


@router.callback_query(F.data.startswith('event_'), StateFilter(ShowEvent.waiting_events_show_end))
async def show_event_details(callback: types.CallbackQuery, state: FSMContext):
    # Получаем номер события из callback_data
    event_num = int(callback.data.split('_')[1])

    data = await state.get_data()
    events = data['events']
    day_offset = data['day_offset']
    user_timezone = data['user_timezone']

    if event_num < 1 or event_num > len(events):
        await callback.answer("Неверный номер события")
        return

    event = events[event_num - 1]
    event['start_dtm'] = (
        datetime.fromisoformat(event['task_start_dtm'])
        .astimezone(pytz.timezone(user_timezone)).strftime("%d.%m.%Y %H:%M")
    )
    event['end_dtm'] = (
        datetime.fromisoformat(event['task_start_dtm'])
        .astimezone(pytz.timezone(user_timezone)).strftime("%d.%m.%Y %H:%M")
    )
    event['task_category'] = map_task_category(event['task_category'])
    # Формируем текст с полным описанием
    text = build_event_full_info(
        event['task_name'],
        event['start_dtm'],
        event['end_dtm'],
        event['task_category'],
        event['task_link'],
        event['task_description']
    )

    # Создаем клавиатуру с действиями
    delete_change_inline_kb = change_delete_task_inline_keyboard(day_offset, event_num)

    # Редактируем сообщение
    await callback.message.edit_text(text, reply_markup=delete_change_inline_kb)
    await callback.answer()


@router.callback_query(F.data.startswith('back_to_list_'), StateFilter(ShowEvent.waiting_events_show_end))
async def back_to_events_list(callback: types.CallbackQuery, state: FSMContext):
    # Получаем смещение из callback_data
    day_offset = int(callback.data.split('_')[-1])
    await state.update_data(day_offset=day_offset)
    # Возвращаемся к списку событий
    await show_events(callback.message, state)
    await callback.answer()


# он забирает айди бота из сообщения вместо айди юзера и еще не удаляет сообщения а новые добавляет




















def setup_calendar_show_tasks_handlers(dp):
    dp.include_router(router)
