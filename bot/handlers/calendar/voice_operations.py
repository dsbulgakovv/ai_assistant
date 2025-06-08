import pytz
import logging
import json
from datetime import datetime, timedelta

from aiogram import Bot, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from .start import StartCalendar
from .show_manual_task import show_events

from texts.calendar import build_event_full_info, build_event_reminder_info
from texts.prompts import system_prompt_calendar
from keyboards.calendar import (
    start_calendar_keyboard,
    task_link_voice_calendar_keyboard,
    task_approval_voice_calendar_keyboard,
    swiping_tasks_no_nums_inline_keyboard,
    swiping_tasks_with_nums_inline_keyboard,
    change_delete_task_inline_keyboard
)
from utils.database_api import DatabaseAPI
from utils.voice_to_text_api import VoiceToTextAPI
from utils.large_lang_model_api import LLMapi

from utils.scheduler import schedule_event, remove_event


logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)

router = Router()
db_api = DatabaseAPI()
v2t_api = VoiceToTextAPI()
llm_api = LLMapi()
MAX_FILE_SIZE = 1 * 1024 * 1024  # = 1MB


class CreateVoiceEvent(StatesGroup):
    waiting_task_link = State()
    waiting_approval = State()


class ChangeEvent(StatesGroup):
    approving_new_event_name = State()
    approving_new_event_category = State()
    approving_new_event_description = State()
    approving_new_event_link = State()
    approving_new_event_start = State()
    approving_new_event_end = State()


# class ShowVoiceEvents(StatesGroup):
#     waiting_events_show_end = State()

class ShowEvent(StatesGroup):
    waiting_events_show_end = State()


def convert_date_string(input_date_str: str, timezone_str: str) -> str:
    dt_naive = datetime.strptime(input_date_str, "%d.%m.%Y %H:%M")
    tz = pytz.timezone(timezone_str)
    dt_local = tz.localize(dt_naive)
    formatted_date = dt_local.strftime("%Y-%m-%d %H:%M:%S.000 %z")

    return formatted_date


def map_weekday(num_day):
    week_days = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье"
    }

    return week_days[num_day]


def map_task_category_from_name(str_category):
    categories_mapping = {
        'Работа': 1,
        'Учеба': 2,
        'Личное': 3,
        'Здоровье': 4,
        'Финансы': 5,
        'Семья': 6
    }

    return categories_mapping[str_category]


def map_task_category_from_key(idx_category):
    categories_mapping = {
        1: 'Работа',
        2: 'Учеба',
        3: 'Личное',
        4: 'Здоровье',
        5: 'Финансы',
        6: 'Семья'
    }
    return categories_mapping[idx_category]


@router.message(StateFilter(StartCalendar.start_calendar))
async def voice_operations_main_calendar_handler(message: types.Message, bot: Bot, state: FSMContext) -> None:
    if message.content_type == types.ContentType.TEXT:
        user_text = message.text
    elif message.content_type in (types.ContentType.VOICE, types.ContentType.AUDIO):
        file_id = message.voice.file_id if message.voice else message.audio.file_id
        file: types.File = await bot.get_file(file_id)
        size = file.file_size or 0
        if size > MAX_FILE_SIZE:
            await message.answer(f"Файл слишком большой ({size / 1024 / 1024:.1f} МБ). "
                                 f"Максимум — {MAX_FILE_SIZE / 1024 / 1024:.1f} МБ.")
            return
        file_name = f"service_files/audio_{file_id}.mp3"
        await bot.download_file(file.file_path, file_name)
        await message.answer('Голосовое сообщение обработано!')
        user_text = await v2t_api.transcript(file_name)
    else:
        await message.answer("Не получается распознать объект")
        return
    user_time_zone = await db_api.get_user_timezone(message.from_user.id)
    await state.update_data(user_timezone=user_time_zone, tg_user_id=message.from_user.id)
    tz = pytz.timezone(user_time_zone)
    current_dtm = datetime.now(tz)
    current_dtm_str = current_dtm.strftime("%Y-%m-%d %H:%M:%S.000 %z")
    messages = [
        {
            "role": "user",
            "content": system_prompt_calendar.format(
                current_dtm_str,
                map_weekday(current_dtm.weekday()),
                user_text
            )
        }
    ]
    llm_json_txt = await llm_api.prompt_answer(messages=messages, temperature=0.05, top_p=0.1, max_tokens=3_000)
    llm_json = json.loads(llm_json_txt['choices'][0]['message']['content'])
    intent = llm_json['intent']
    if intent == 'create_task':
        llm_data = llm_json['data']
        await message.answer(
            "Добавим ссылку на встречу?",
            reply_markup=task_link_voice_calendar_keyboard()
        )
        await state.update_data(llm_data=llm_data)
        await state.set_state(CreateVoiceEvent.waiting_task_link)
    elif intent == 'show_tasks':
        llm_data = llm_json['data']
        await state.update_data(show_dt=llm_data['show_dt'])
        await show_events(message, state)
        await state.set_state(ShowEvent.waiting_events_show_end)
    elif intent == 'unrecognized':
        await message.answer("Не получается распознать желаемое действие")


@router.message(StateFilter(CreateVoiceEvent.waiting_task_link))
async def voice_operations_create_task_calendar_handler(message: types.Message, state: FSMContext) -> None:
    if message.text.lower() == 'отмена':
        await message.answer(
            "Создание события отменено",
            reply_markup=start_calendar_keyboard()
        )
        await state.clear()
        await state.set_state(StartCalendar.start_calendar)
        return
    else:
        if message.text.lower() == 'без ссылки':
            task_link = 'Нет ссылки на событие'
        else:
            task_link = message.text
        data = await state.get_data()
        task_data = data['llm_data']
        task_data['task_link'] = task_link
        await state.update_data(llm_data=task_data)
        await message.answer(
            build_event_full_info(
                task_data.get('task_name'),
                task_data.get('start_dtm'),
                task_data.get('end_dtm'),
                task_data.get('task_category'),
                task_data.get('task_link'),
                task_data.get('task_description')
            ),
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            "Все верно?",
            reply_markup=task_approval_voice_calendar_keyboard()
        )
        await state.set_state(CreateVoiceEvent.waiting_approval)


@router.message(StateFilter(CreateVoiceEvent.waiting_approval))
async def voice_operations_create_success_calendar_handler(message: types.Message, state: FSMContext) -> None:
    if message.text.lower() == 'отмена':
        await message.answer(
            "Создание события отменено",
            reply_markup=start_calendar_keyboard()
        )
        await state.clear()
        await state.set_state(StartCalendar.start_calendar)
        return
    elif message.text.lower() == 'подтвердить':
        data = await state.get_data()
        task_data = data['llm_data']
        response, status = await db_api.create_task(
            message.from_user.id,
            task_data['task_name'], 1, map_task_category_from_name(task_data['task_category']),
            task_data['task_description'], task_data['task_link'],
            convert_date_string(task_data['start_dtm'], data['user_timezone']),
            convert_date_string(task_data['end_dtm'], data['user_timezone'])
        )
        # ---------- scheduler create ----------
        from core import bot, scheduler
        run_datetime_30 = datetime.strptime(task_data['start_dtm'], '%d.%m.%Y %H:%M') - timedelta(minutes=30)
        text_30 = build_event_reminder_info(
            title=task_data['task_name'], min_left=30,
            link=task_data['task_link'], description=task_data['task_description']
        )
        schedule_event(
            scheduler=scheduler, event_id=response['task_id'] + 30,
            run_datetime=run_datetime_30, bot=bot, chat_id=message.chat.id, text=text_30
        )
        run_datetime_5 = datetime.strptime(task_data['start_dtm'], '%d.%m.%Y %H:%M') - timedelta(minutes=5)
        text_5 = build_event_reminder_info(
            title=task_data['task_name'], min_left=5,
            link=task_data['task_link'], description=task_data['task_description']
        )
        schedule_event(
            scheduler=scheduler, event_id=response['task_id'] + 5,
            run_datetime=run_datetime_5, bot=bot, chat_id=message.chat.id, text=text_5
        )
        # ---------------------------------------
        if status == 201:
            await state.clear()
            await message.answer(
                "✅ Событие успешно создано!",
                reply_markup=start_calendar_keyboard()
            )
            await state.clear()
            await state.set_state(StartCalendar.start_calendar)
        else:
            await message.answer(
                f"INTERNAL SERVER ERROR.\n"
                f"Please, contact support https://t.me/dm1trybu",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.clear()
            await state.set_state(None)


def setup_calendar_voice_operations_handlers(dp):
    dp.include_router(router)
