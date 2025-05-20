import pytz
import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from aiogram import F, Router, types
from aiogram.filters import StateFilter, or_f
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
    change_delete_task_inline_keyboard,
    choice_change_task_inline_keyboard,
    editing_approve_task,
    task_category_change_calendar_keyboard,
    task_dtm_change_calendar_keyboard,
    deleting_task_inline_keyboard
)
from utils.database_api import DatabaseAPI

logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)

router = Router()
db_api = DatabaseAPI()


class ShowEvent(StatesGroup):
    waiting_events_show_end = State()


class ChangeEvent(StatesGroup):
    approving_new_event_name = State()
    approving_new_event_category = State()
    approving_new_event_description = State()
    approving_new_event_link = State()
    approving_new_event_start = State()
    approving_new_event_end = State()


class DeleteEvent(StatesGroup):
    approving_event_delete = State()


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


def map_task_category_from_str(str_category):
    categories_mapping = {
        'Работа': 1,
        'Учеба': 2,
        'Личное': 3,
        'Здоровье': 4,
        'Финансы': 5,
        'Семья': 6
    }
    return categories_mapping[str_category]


def convert_date_string(input_date_str: str, timezone_str: str) -> str:
    dt_naive = datetime.strptime(input_date_str, "%d.%m.%Y %H:%M")
    tz = pytz.timezone(timezone_str)
    dt_local = tz.localize(dt_naive)
    formatted_date = dt_local.strftime("%Y-%m-%d %H:%M:%S.000 %z")
    return formatted_date


def convert_date_string_to_iso_utc(input_date_str: str, timezone_str: str) -> str:
    dt_naive = datetime.strptime(input_date_str, "%d.%m.%Y %H:%M")
    local_tz = ZoneInfo(timezone_str)
    dt_local = dt_naive.replace(tzinfo=local_tz)
    dt_utc = dt_local.astimezone(timezone.utc)
    return dt_utc.isoformat()


def localize_db_date(input_date_str: str, timezone_str: str) -> str:
    local_dtm = (
        datetime.fromisoformat(input_date_str)
        .astimezone(pytz.timezone(timezone_str))
        .strftime("%Y-%m-%d %H:%M:%S.000 %z")
    )
    return local_dtm


def convert_to_business_dt(input_date_str: str, timezone_str: str) -> str:
    formatted_date = (
        datetime.fromisoformat(input_date_str)
        .astimezone(pytz.timezone(timezone_str))
        .strftime("%Y-%m-%d")
    )
    return formatted_date


def days_diff(date1, date2):
    d1 = datetime.strptime(date1, "%Y-%m-%d").date()
    d2 = datetime.strptime(date2, "%Y-%m-%d").date()
    return abs((d2 - d1).days)


def get_rounded_datetime(user_time_zone):
    utc_time = datetime.now(timezone.utc)
    local_time = utc_time.astimezone(pytz.timezone(user_time_zone))

    # Округляем до ближайших 30 минут
    minute = local_time.minute
    if minute < 15:
        # Округляем вниз до полного часа
        rounded = local_time.replace(minute=0, second=0, microsecond=0)
    elif 15 <= minute < 45:
        # Округляем до 30 минут
        rounded = local_time.replace(minute=30, second=0, microsecond=0)
    else:
        # Округляем вверх до следующего часа
        rounded = (local_time.replace(minute=0, second=0, microsecond=0)
                   + timedelta(hours=1))

    next_rounded = rounded + timedelta(minutes=30)

    # Форматируем в строку дд.мм.гггг чч:мм
    formatted_cur = rounded.strftime("%d.%m.%Y %H:%M")
    formatted_next = next_rounded.strftime("%d.%m.%Y %H:%M")

    return formatted_cur, formatted_next


# ------------------------ SHOWING EVENTS ------------------------
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


@router.message(
    or_f(
        StateFilter(ChangeEvent.approving_new_event_name), StateFilter(ChangeEvent.approving_new_event_category),
        StateFilter(ChangeEvent.approving_new_event_description), StateFilter(ChangeEvent.approving_new_event_link),
        StateFilter(ChangeEvent.approving_new_event_start), StateFilter(ChangeEvent.approving_new_event_end),
        StateFilter(ShowEvent.waiting_events_show_end)
    ),
    F.text.casefold() == 'вернуться назад'
)
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
        await state.update_data(day_offset=day_offset, cur_date=cur_date.strftime("%Y-%m-%d"))

    target_date_str = (cur_date + timedelta(days=day_offset)).strftime("%d.%m.%Y")
    target_date_query = (cur_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")

    # Здесь получаем события из вашего API/Redis
    events, status = await db_api.get_tasks(data['tg_user_id'], target_date_query, target_date_query)
    await state.update_data(events=events)

    # Если событий нет
    if status == 404:
        left_right_inline_no_nums_kb = swiping_tasks_no_nums_inline_keyboard(day_offset)
        text = f"На <b>{target_date_str}</b> событий нет"
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
    text = f"События на <b>{target_date_str}</b>\n\n"
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
    data = await state.get_data()
    current_offset = data['day_offset']

    # Вычисляем новое смещение
    new_offset = current_offset - 1 if direction == "prev" else current_offset + 1
    await state.update_data(day_offset=new_offset)

    # "Переотправляем" сообщение с новым смещением
    await show_events(callback.message, state)
    await callback.answer()


def form_one_event_detailed(event: dict, user_timezone: str) -> str:
    event['start_dtm'] = (
        datetime.fromisoformat(event['task_start_dtm'])
        .astimezone(pytz.timezone(user_timezone)).strftime("%d.%m.%Y %H:%M")
    )
    event['end_dtm'] = (
        datetime.fromisoformat(event['task_end_dtm'])
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
    return text


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
    text = form_one_event_detailed(event, user_timezone)

    # Создаем клавиатуру с действиями
    delete_change_inline_kb = change_delete_task_inline_keyboard(day_offset, event_num)

    # Редактируем сообщение
    await callback.message.edit_text(text, reply_markup=delete_change_inline_kb)
    await state.update_data(one_event_text=text)
    await callback.answer()
# ----------------------------------------------------------------


# ------------------------ CHANGING EVENT ------------------------
@router.callback_query(F.data.startswith('edit_'), StateFilter(ShowEvent.waiting_events_show_end))
async def edit_event_start(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    event_num = int(callback.data.split('_')[-1])
    await state.update_data(editing_event_num=event_num)
    await callback.message.edit_text(data['one_event_text'], reply_markup=choice_change_task_inline_keyboard())
    await callback.answer()


# NAME
@router.callback_query(F.data.startswith('editing_task_name'), StateFilter(ShowEvent.waiting_events_show_end))
async def editing_task_name_event_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите новое название", reply_markup=None)
    await callback.answer()
    await state.set_state(ChangeEvent.approving_new_event_name)


@router.message(StateFilter(ChangeEvent.approving_new_event_name))
async def editing_task_name_event_next(message: types.Message, state: FSMContext):
    new_name = message.text
    data = await state.get_data()
    user_timezone = data['user_timezone']
    event = data['events'][data['editing_event_num'] - 1]
    new_event_info = event.copy()
    new_event_info['task_name'] = new_name
    new_text = form_one_event_detailed(new_event_info, user_timezone)
    await state.update_data(new_event_info=new_event_info)
    await message.answer(new_text, reply_markup=editing_approve_task())
    await state.update_data(one_event_text=new_text)
    await state.set_state(ShowEvent.waiting_events_show_end)


# CATEGORY
@router.callback_query(F.data.startswith('editing_task_category'), StateFilter(ShowEvent.waiting_events_show_end))
async def editing_task_category_event_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выберите новую категорию", reply_markup=task_category_change_calendar_keyboard())
    await callback.answer()
    await state.set_state(ChangeEvent.approving_new_event_category)


@router.callback_query(F.data.startswith('task_category_'), StateFilter(ChangeEvent.approving_new_event_category))
async def editing_task_category_event_next(callback: types.CallbackQuery, state: FSMContext):
    new_category_int = int(callback.data.split('_')[-1])
    data = await state.get_data()
    user_timezone = data['user_timezone']
    event = data['events'][data['editing_event_num'] - 1]
    new_event_info = event.copy()
    new_event_info['task_category'] = new_category_int
    new_text = form_one_event_detailed(new_event_info, user_timezone)
    await state.update_data(new_event_info=new_event_info)
    await callback.message.edit_text(new_text, reply_markup=editing_approve_task())
    await state.update_data(one_event_text=new_text)
    await state.set_state(ShowEvent.waiting_events_show_end)


# DESCRIPTION
@router.callback_query(F.data.startswith('editing_task_description'), StateFilter(ShowEvent.waiting_events_show_end))
async def editing_task_description_event_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите новое описание", reply_markup=None)
    await callback.answer()
    await state.set_state(ChangeEvent.approving_new_event_description)


@router.message(StateFilter(ChangeEvent.approving_new_event_description))
async def editing_task_description_event_next(message: types.Message, state: FSMContext):
    new_description = message.text
    data = await state.get_data()
    user_timezone = data['user_timezone']
    event = data['events'][data['editing_event_num'] - 1]
    new_event_info = event.copy()
    new_event_info['task_description'] = new_description
    new_text = form_one_event_detailed(new_event_info, user_timezone)
    await state.update_data(new_event_info=new_event_info)
    await message.answer(new_text, reply_markup=editing_approve_task())
    await state.update_data(one_event_text=new_text)
    await state.set_state(ShowEvent.waiting_events_show_end)


# LINK
@router.callback_query(F.data.startswith('editing_task_link'), StateFilter(ShowEvent.waiting_events_show_end))
async def editing_task_link_event_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите новую ссылку", reply_markup=None)
    await callback.answer()
    await state.set_state(ChangeEvent.approving_new_event_link)


@router.message(StateFilter(ChangeEvent.approving_new_event_link))
async def editing_task_link_event_next(message: types.Message, state: FSMContext):
    new_link = message.text
    data = await state.get_data()
    user_timezone = data['user_timezone']
    event = data['events'][data['editing_event_num'] - 1]
    new_event_info = event.copy()
    new_event_info['task_link'] = new_link
    new_text = form_one_event_detailed(new_event_info, user_timezone)
    await state.update_data(new_event_info=new_event_info)
    await message.answer(new_text, reply_markup=editing_approve_task())
    await state.update_data(one_event_text=new_text)
    await state.set_state(ShowEvent.waiting_events_show_end)


# START DTM
@router.callback_query(F.data.startswith('editing_start_dtm'), StateFilter(ShowEvent.waiting_events_show_end))
async def editing_task_start_event_start(callback: types.CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    await callback.message.delete()
    await callback.message.answer(
        f"Выбери новую дату и время начала события.\n",
        reply_markup=task_dtm_change_calendar_keyboard()
    )
    await dialog_manager.start(
        CalendarState.select_date,
        mode=StartMode.RESET_STACK
    )
    await callback.answer()
    await state.set_state(ChangeEvent.approving_new_event_start)


@router.message(StateFilter(ChangeEvent.approving_new_event_start))
async def editing_task_start_event_next(message: types.Message, state: FSMContext):
    if message.text.lower() == 'дальше':
        data = await state.get_data()
        selected_datetime = data.get("event_datetime")
        await state.update_data(event_datetime=None)
        await state.update_data(start_dtm=selected_datetime)
        after_selected_datetime = (
                datetime.strptime(selected_datetime, "%d.%m.%Y %H:%M") + timedelta(minutes=30)
        ).strftime("%d.%m.%Y %H:%M")
        await state.update_data(end_dtm=after_selected_datetime)

        # data = await state.get_data()
        user_timezone = data['user_timezone']
        event = data['events'][data['editing_event_num'] - 1]
        new_event_info = event.copy()
        new_event_info['task_start_dtm'] = convert_date_string_to_iso_utc(selected_datetime, user_timezone)
        new_event_info['task_end_dtm'] = convert_date_string_to_iso_utc(after_selected_datetime, user_timezone)
        new_text = form_one_event_detailed(new_event_info, user_timezone)
        await state.update_data(new_event_info=new_event_info)
        msg = await message.answer(new_text, reply_markup=editing_approve_task())
        await state.update_data(one_event_text=new_text, events_message_id=msg.message_id)
        await state.set_state(ShowEvent.waiting_events_show_end)
    else:
        await message.answer("Такой опции нет")


# END DTM
@router.callback_query(F.data.startswith('editing_end_dtm'), StateFilter(ShowEvent.waiting_events_show_end))
async def editing_task_end_event_start(callback: types.CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    await callback.message.delete()
    await callback.message.answer(
        f"Выбери новую дату и время завершения события.\n",
        reply_markup=task_dtm_change_calendar_keyboard()
    )
    await dialog_manager.start(
        CalendarState.select_date,
        mode=StartMode.RESET_STACK
    )
    await callback.answer()
    await state.set_state(ChangeEvent.approving_new_event_end)


@router.message(StateFilter(ChangeEvent.approving_new_event_end))
async def editing_task_end_event_next(message: types.Message, state: FSMContext, dialog_manager: DialogManager):
    if message.text.lower() == 'дальше':
        data = await state.get_data()
        selected_datetime = data.get("event_datetime")
        await state.update_data(event_datetime=None)
        user_timezone = data['user_timezone']
        startd_dtm = datetime.fromisoformat(
            data['events'][data['editing_event_num'] - 1]['task_start_dtm']
        ).astimezone(pytz.timezone(user_timezone))
        end_dtm = datetime.strptime(selected_datetime, "%d.%m.%Y %H:%M").replace(tzinfo=ZoneInfo(user_timezone))
        if end_dtm > startd_dtm:
            await message.answer(
                f"Неверно выбрана дата завершения\n"
                f"Выбери новую дату и время завершения события.",
                reply_markup=task_dtm_change_calendar_keyboard()
            )
            await dialog_manager.start(
                CalendarState.select_date,
                mode=StartMode.RESET_STACK
            )
            await state.set_state(ChangeEvent.approving_new_event_end)
        await state.update_data(end_dtm=selected_datetime)
        # data = await state.get_data()
        event = data['events'][data['editing_event_num'] - 1]
        new_event_info = event.copy()
        new_event_info['task_end_dtm'] = convert_date_string_to_iso_utc(selected_datetime, user_timezone)
        new_text = form_one_event_detailed(new_event_info, user_timezone)
        await state.update_data(new_event_info=new_event_info)
        msg = await message.answer(new_text, reply_markup=editing_approve_task())
        await state.update_data(one_event_text=new_text, events_message_id=msg.message_id)
        await state.set_state(ShowEvent.waiting_events_show_end)
    else:
        await message.answer("Такой опции нет")


# UNIVERSAL IN EDIT MODE
@router.callback_query(F.data.startswith('approve_new_edit'), StateFilter(ShowEvent.waiting_events_show_end))
async def approved_save_editing_task(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(events_message_id=callback.message.message_id)
    data = await state.get_data()
    event = data['new_event_info']
    task_global_id = event['id']
    business_dt = convert_to_business_dt(event['task_start_dtm'], data['user_timezone'])
    logger.info({'task_start_dtm': event['task_start_dtm'], 'business_dt': business_dt})
    task_start_dtm = localize_db_date(event['task_start_dtm'], data['user_timezone'])
    task_end_dtm = localize_db_date(event['task_end_dtm'], data['user_timezone'])

    _, status = await db_api.update_task(
        task_global_id=task_global_id, task_name=event['task_name'],
        task_status=2, task_category=map_task_category_from_str(event['task_category']),
        task_description=event['task_description'], task_link=event['task_link'],
        task_start_dtm=task_start_dtm, task_end_dtm=task_end_dtm
    )

    if status == 200:
        await callback.message.answer(
            "✅ Событие успешно обновлено!",
            reply_markup=only_back_to_manual_calendar_menu_keyboard()
        )
    elif status == 404:
        await callback.message.answer(
            "Неверно выбрана дата завершения"
        )
        return
    else:
        await callback.message.answer(
            f"INTERNAL SERVER ERROR.\n"
            f"Please, contact support https://t.me/dm1trybu"
        )
        return
    delete_change_inline_kb = change_delete_task_inline_keyboard(data['day_offset'], data['editing_event_num'])
    events, _ = await db_api.get_tasks(data['tg_user_id'], business_dt, business_dt)

    result = next(filter(lambda x: x["id"] == task_global_id, events), None)
    new_task_relative_id = result['task_relative_id']

    new_day_offset = days_diff(data['cur_date'], business_dt)

    await state.update_data(
        events=events, editing_event_num=new_task_relative_id, day_offset=new_day_offset
    )
    await callback.message.delete()
    msg = await callback.message.answer(data['one_event_text'], reply_markup=delete_change_inline_kb)
    await state.update_data(events_message_id=msg.message_id)
    await callback.answer()


@router.callback_query(F.data.startswith('back_to_change_delete_task'), StateFilter(ShowEvent.waiting_events_show_end))
async def back_to_events_list(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    delete_change_inline_kb = change_delete_task_inline_keyboard(data['day_offset'], data['editing_event_num'])
    await callback.message.edit_text(data['one_event_text'], reply_markup=delete_change_inline_kb)
    await callback.answer()
# ----------------------------------------------------------------


# -------------------------- DELETE TASK -------------------------
@router.callback_query(F.data.startswith('delete_'), StateFilter(ShowEvent.waiting_events_show_end))
async def delete_event_start(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    event_num = int(callback.data.split('_')[-1])
    await state.update_data(editing_event_num=event_num)
    await callback.message.edit_text(data['one_event_text'], reply_markup=deleting_task_inline_keyboard())
    await state.set_state(DeleteEvent.approving_event_delete)
    await callback.answer()


@router.callback_query(F.data.startswith('deleting_task'), StateFilter(DeleteEvent.approving_event_delete))
async def delete_event_approved(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    event = data['events'][data['editing_event_num'] - 1]
    task_global_id = event['id']
    response, status = await db_api.delete_task(task_global_id)
    if status == 200:
        await callback.message.delete()
        await callback.message.answer(
            "✅ Событие успешно удалено!",
            reply_markup=only_back_to_manual_calendar_menu_keyboard()
        )
    elif status == 404:
        await callback.message.answer(
            "Событие не найдено",
            reply_markup=only_back_to_manual_calendar_menu_keyboard()
        )
    else:
        await callback.message.answer(
            f"INTERNAL SERVER ERROR.\n"
            f"Please, contact support https://t.me/dm1trybu"
        )
        return
    # Возвращаемся к списку событий
    await state.set_state(ShowEvent.waiting_events_show_end)
    await show_events(callback.message, state)
    await callback.answer()


@router.callback_query(F.data.startswith('back_to_delete_task_choice'), StateFilter(DeleteEvent.approving_event_delete))
async def back_to_events_list(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    delete_change_inline_kb = change_delete_task_inline_keyboard(data['day_offset'], data['editing_event_num'])
    await callback.message.edit_text(data['one_event_text'], reply_markup=delete_change_inline_kb)
    await callback.answer()
# ----------------------------------------------------------------


# ---------------------------- GO BACK ---------------------------
@router.callback_query(F.data.startswith('back_to_list_'), StateFilter(ShowEvent.waiting_events_show_end))
async def back_to_events_list(callback: types.CallbackQuery, state: FSMContext):
    # Получаем смещение из callback_data
    day_offset = int(callback.data.split('_')[-1])
    await state.update_data(day_offset=day_offset)
    # Возвращаемся к списку событий
    await show_events(callback.message, state)
    await callback.answer()
# ----------------------------------------------------------------


def setup_calendar_show_tasks_handlers(dp):
    dp.include_router(router)
