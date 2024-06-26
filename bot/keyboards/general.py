from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def start_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Расшифровка голоса")
    kb.button(text="Что-то еще")
    kb.button(text="Хватит")
    return kb.as_markup(resize_keyboard=True)


def end_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Хватит")
    return kb.as_markup(resize_keyboard=True)
