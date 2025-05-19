from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from keyboards.general import start_keyboard
from utils.database_api import DatabaseAPI
from texts import instructions

import logging


db_api = DatabaseAPI()
router = Router()


logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)


class InitStates(StatesGroup):
    started = State()


@router.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext) -> None:
    resp, status = await db_api.get_user(message.from_user.id)
    if status == 404:
        user_info = {
            'tg_user_id': message.from_user.id, 'username': message.from_user.username,
            'full_name': message.from_user.full_name, 'timezone': 'Europe/Moscow', 'lang': 'rus'
        }
        logger.info(user_info)
        post_resp, post_status = await db_api.create_user(
            **user_info
            # message.from_user.id,
            # message.from_user.username,
            # message.from_user.full_name,
            # 'Europe/Moscow',
            # 'rus'
        )
        if post_status == 201:
            await message.answer(
                f"Привет, {message.from_user.full_name}!\n"
                "Профиль создан. Теперь ты можешь ознакомиться с функционалом и начать пользоваться."
            )
            await message.answer(
                instructions.start_instruction
            )
            await message.answer(
                f"Я виртуальный секретарь.\n"
                "Выбери нужное действие.",
                reply_markup=start_keyboard()
            )
    elif status == 200:
        await message.answer(
            f"Привет, {message.from_user.full_name}!\n"
            "Виртуальный секретарь на связи.\n"
            "Выбери нужное действие.",
            reply_markup=start_keyboard()
        )
    else:
        await message.answer(
            f"INTERNAL SERVER ERROR.\n"
            f"Please, contact support https://t.me/dm1trybu",
            reply_markup=ReplyKeyboardRemove()
        )
    await state.clear()
    await state.set_state(None)


@router.message(Command('help'))
async def command_help_handler(message: types.Message, state: FSMContext) -> None:
    msg = (
        instructions.start_instruction
    )
    await message.answer(msg, reply_markup=start_keyboard())
    await state.clear()
    await state.set_state(None)


@router.message(F.text.casefold() == 'вернуться в меню')
async def process_end_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Выбери нужное действие",
        reply_markup=start_keyboard()
    )
    await state.clear()
    await state.set_state(None)


def setup_start_handlers(dp):
    dp.include_router(router)
