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
    kb.row(KeyboardButton(text='Без названия'))
    kb.row(KeyboardButton(text='Отмена'))
    return kb.as_markup(resize_keyboard=True)


def task_category_manual_calendar_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Личное'))
    kb.add(KeyboardButton(text='Работа'))
    kb.row(KeyboardButton(text='Учеба'))
    kb.add(KeyboardButton(text='Семья'))
    kb.row(KeyboardButton(text='Здоровье'))
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


def task_link_manual_calendar_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Без ссылки'))
    kb.row(KeyboardButton(text='К предыдущему шагу'))
    kb.row(KeyboardButton(text='Отмена'))
    return kb.as_markup(resize_keyboard=True)


def task_start_dt_manual_calendar_keyboard() -> (InlineKeyboardMarkup, ReplyKeyboardMarkup):
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Дальше'))
    kb.row(KeyboardButton(text='К предыдущему шагу'))
    kb.row(KeyboardButton(text='Отмена'))

    return kb.as_markup(resize_keyboard=True)


def task_duration_manual_calendar_keyboard() -> (InlineKeyboardMarkup, ReplyKeyboardMarkup):
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Дальше'))
    kb.row(KeyboardButton(text='Изменить дату завершения'))
    kb.row(KeyboardButton(text='К предыдущему шагу'))
    kb.row(KeyboardButton(text='Отмена'))

    return kb.as_markup(resize_keyboard=True)


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
