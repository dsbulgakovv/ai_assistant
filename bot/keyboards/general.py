from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def start_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Мой календарь'))
    kb.row(KeyboardButton(text='Расшифровка голоса'))
    kb.row(KeyboardButton(text='Задать вопрос'))
    return kb.as_markup(resize_keyboard=True)


def end_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Вернуться в меню')
    return kb.as_markup(resize_keyboard=True)
