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
def swiping_tasks_with_nums_inline_keyboard(events: list, day_offset: int) -> InlineKeyboardMarkup:
    # Создаем список кнопок
    buttons = list()

    # Добавляем кнопки навигации по дням
    buttons.append([
        InlineKeyboardButton(text="←", callback_data=f"prev_day_{day_offset}"),
        InlineKeyboardButton(text="→", callback_data=f"next_day_{day_offset}")
    ])

    # Добавляем кнопки с номерами событий
    if events:
        event_buttons = [
            InlineKeyboardButton(text=str(i), callback_data=f"event_{i}_{day_offset}")
            for i in range(1, len(events) + 1)
        ]
        buttons.append(event_buttons)

    # Создаем клавиатуру с кнопками
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def swiping_tasks_no_nums_inline_keyboard(day_offset: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="←", callback_data=f"prev_day_{day_offset}"),
            InlineKeyboardButton(text="→", callback_data=f"next_day_{day_offset}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def change_delete_task_inline_keyboard(day_offset: int, event_num: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Изменить", callback_data=f"edit_{event_num}"),
            InlineKeyboardButton(text="Удалить", callback_data=f"delete_{event_num}")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=f"back_to_list_{day_offset}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def choice_change_task_inline_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Дату и время начала ", callback_data=f"editing_start_dtm")],
        [InlineKeyboardButton(text="Дату и время завершения", callback_data=f"editing_end_dtm")],
        [
            InlineKeyboardButton(text="Название", callback_data=f"editing_task_name"),
            InlineKeyboardButton(text="Категорию", callback_data=f"editing_task_category")
        ],
        [
            InlineKeyboardButton(text="Ссылку", callback_data=f"editing_task_link"),
            InlineKeyboardButton(text="Описание", callback_data=f"editing_task_description")
        ],
        [InlineKeyboardButton(text="Назад", callback_data=f"back_to_list_")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def only_back_to_manual_calendar_menu_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Вернуться назад'))
    return kb.as_markup(resize_keyboard=True)
# -----------------------------------------
