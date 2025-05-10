from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def start_calendar_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Мануальный режим'))
    kb.row(KeyboardButton(text='Вернуться в меню'))
    return kb.as_markup(resize_keyboard=True)


def start_manual_calendar_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Создать новое событие'))
    kb.row(KeyboardButton(text='Посмотреть предстоящие события'))
    kb.row(KeyboardButton(text='Изменить/удалить событие'))
    kb.row(KeyboardButton(text='Вернуться в меню'))
    return kb.as_markup(resize_keyboard=True)


def task_name_manual_calendar_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Стандартное название'))
    kb.row(KeyboardButton(text='Отмена'))
    return kb.as_markup(resize_keyboard=True)


def task_category_manual_calendar_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='Личное'))
    kb.add(KeyboardButton(text='Работа'))
    kb.add(KeyboardButton(text='Учеба'))
    kb.row()
    kb.add(KeyboardButton(text='Семья'))
    kb.add(KeyboardButton(text='Здоровье'))
    kb.add(KeyboardButton(text='Финансы'))
    kb.row(KeyboardButton(text='К предыдущему шагу'))
    kb.row(KeyboardButton(text='Отмена'))
    return kb.as_markup(resize_keyboard=True)


def task_description_manual_calendar_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Без описания'))
    kb.row(KeyboardButton(text='К предыдущему шагу'))
    kb.row(KeyboardButton(text='Отмена'))
    return kb.as_markup(resize_keyboard=True)


def task_start_dtm_manual_calendar_keyboard() -> (InlineKeyboardMarkup, ReplyKeyboardMarkup):
    start_button_1 = InlineKeyboardButton(text="В ближайший час", callback_data="15_min")
    show_start_inline_kb = InlineKeyboardMarkup(inline_keyboard=[[start_button_1]])

    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Дальше'))
    kb.row(KeyboardButton(text='К предыдущему шагу'))
    kb.row(KeyboardButton(text='Отмена'))

    return {'inline': show_start_inline_kb, 'reply': kb.as_markup(resize_keyboard=True)}


def task_duration_manual_calendar_keyboard() -> (InlineKeyboardMarkup, ReplyKeyboardMarkup):
    dur_button_1 = InlineKeyboardButton(text="15 мин", callback_data="15_min")
    dur_button_2 = InlineKeyboardButton(text="30 мин", callback_data="30_min")
    dur_button_3 = InlineKeyboardButton(text="1 час", callback_data="60_min")
    dur_button_4 = InlineKeyboardButton(text="2 часа", callback_data="120_min")
    dur_button_5 = InlineKeyboardButton(text="3 часа", callback_data="180_min")
    dur_button_6 = InlineKeyboardButton(text="До конца дня", callback_data="all_rest")
    show_dur_inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [dur_button_1, dur_button_2, dur_button_3],
        [dur_button_4, dur_button_5, dur_button_6]
    ])

    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Дальше'))
    kb.row(KeyboardButton(text='К предыдущему шагу'))
    kb.row(KeyboardButton(text='Отмена'))

    return {'inline': show_dur_inline_kb, 'reply': kb.as_markup(resize_keyboard=True)}


def task_approval_manual_calendar_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Подтвердить'))
    kb.row(KeyboardButton(text='К предыдущему шагу'))
    kb.row(KeyboardButton(text='Отмена'))
    return kb.as_markup(resize_keyboard=True)


def cancel_process_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='К предыдущему шагу'))
    kb.row(KeyboardButton(text='Отмена'))
    return kb.as_markup(resize_keyboard=True)
