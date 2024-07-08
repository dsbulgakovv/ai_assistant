import asyncio
import logging
import sys

from datetime import date

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BotCommand, BotCommandScopeDefault, ReplyKeyboardRemove
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from keyboards.general import start_keyboard
from handlers import voice_to_text, q_and_a


TOKEN = '6675850647:AAGMrJUk2t4CV2oHwtz7QNxrR0vPn30Bbac'

dp = Dispatcher(storage=MemoryStorage())
dp['user_data'] = {'last_start_cmd_usage': '1999-01-01'}

router = Router()

logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)


class InitStates(StatesGroup):
    start = State()


@dp.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext, user_data: dict) -> None:
    if user_data['last_start_cmd_usage'] == str(date.today()):
        await state.set_state(InitStates.start)
        await message.answer(
            "Я виртуальный ассистент.\nВыбери нужное действие.",
            reply_markup=start_keyboard()
        )
    else:
        user_data['last_start_cmd_usage'] = str(date.today())
        await state.set_state(InitStates.start)
        await message.answer(
            f"Привет, {message.from_user.full_name}!\n"
            "Я виртуальный ассистент.\nВыбери нужное действие.",
            reply_markup=start_keyboard()
        )


@dp.message(Command('help'))
async def command_help_handler(message: types.Message, state: FSMContext) -> None:
    msg = (
        "Бот умеет:\n"
        "- расшифровывать аудио сообщение\n"
        "- что-то еще"
    )
    await message.answer(msg)
    await state.set_state(None)


@dp.message(F.text.casefold() == 'хватит')
async def process_end_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer('Закончили', reply_markup=ReplyKeyboardRemove())
    await state.clear()


@dp.message(StateFilter(None), ~(F.text.casefold() == 'расшифровка голоса'), ~(F.text.casefold() == 'задать вопрос'))
async def uncertainty_handler(message: types.Message) -> None:
    await message.answer(f"Выбери нужную функцию!")


async def set_commands(bot: Bot):
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='help', description='Справка')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def main() -> None:
    dp.include_routers(voice_to_text.router, q_and_a.router)
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
