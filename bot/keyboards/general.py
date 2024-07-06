from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def start_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Расшифровка голоса')
    kb.button(text='Задать вопрос')
    kb.button(text='Хватит')
    return kb.as_markup(resize_keyboard=True)


def end_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Хватит')
    return kb.as_markup(resize_keyboard=True)
