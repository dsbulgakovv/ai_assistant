from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


# ------ START CALENDAR INTERACTION ------
def start_calendar_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Мануальный режим'))
    kb.row(KeyboardButton(text='Вернуться в меню'))
    return kb.as_markup(resize_keyboard=True)


def start_manual_calendar_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Создать новое событие'))
    kb.row(KeyboardButton(text='Посмотреть предстоящие события'))
    kb.row(KeyboardButton(text='Вернуться в меню'))
    return kb.as_markup(resize_keyboard=True)
# -----------------------------------------


# ------ MANUAL TASK CREATION INTERACTION ------
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


def task_start_dt_manual_calendar_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Дальше'))
    kb.row(KeyboardButton(text='К предыдущему шагу'))
    kb.row(KeyboardButton(text='Отмена'))

    return kb.as_markup(resize_keyboard=True)


def task_duration_manual_calendar_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Дальше'))
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
# -----------------------------------------


# ------ MANUAL TASK SHOW INTERACTION ------
def swiping_tasks_with_nums_inline_keyboard(events, day_offset) -> InlineKeyboardMarkup:
    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup()

    # Кнопки переключения дней
    keyboard.row(
        InlineKeyboardButton("←", callback_data=f"prev_day_{day_offset}"),
        InlineKeyboardButton("→", callback_data=f"next_day_{day_offset}")
    )

    # Кнопки с номерами событий
    event_buttons = [
        InlineKeyboardButton(str(i), callback_data=f"event_{i}_{day_offset}")
        for i in range(1, len(events) + 1)
    ]
    return keyboard.row(*event_buttons)


def swiping_tasks_no_nums_inline_keyboard(day_offset) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("←", callback_data=f"prev_day_{day_offset}"),
        InlineKeyboardButton("→", callback_data=f"next_day_{day_offset}")
    )
    return keyboard


def change_delete_task_inline_keyboard(event_num) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Изменить", callback_data=f"edit_{event_num}"),
        InlineKeyboardButton("Удалить", callback_data=f"delete_{event_num}")
    )
    keyboard.add(InlineKeyboardButton("Назад", callback_data=f"back_to_list_{day_offset}"))
    return keyboard


def only_back_to_manual_calendar_menu_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Вернуться в меню'))
    return kb.as_markup(resize_keyboard=True)
# -----------------------------------------
