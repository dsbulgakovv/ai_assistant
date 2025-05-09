import logging
import os

from aiogram import Bot, F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from keyboards.general import start_keyboard, end_keyboard
from utils.voice_to_text_api import VoiceToTextAPI


logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)

markup_text = "**Текст:**\n{}"

router = Router()
api = VoiceToTextAPI()


class VoiceToText(StatesGroup):
    standard_script = State()


@router.message(F.text.casefold() == 'расшифровка голоса')
async def voice_to_text_start_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Запиши мне голосовое сообщение и я пришлю его расшифровку.",
        reply_markup=end_keyboard()
    )
    await state.set_state(VoiceToText.standard_script)


@router.message(StateFilter(VoiceToText.standard_script))
async def voice_to_text_process_handler(message: types.Message, bot: Bot, state: FSMContext) -> None:
    if message.voice:
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_name = f"service_files/audio_{file_id}.mp3"
        await bot.download_file(file_path, file_name)
        await message.answer('Голосовое сообщение обработано!', reply_markup=end_keyboard())
        logger.info(os.listdir('./service_files'))
        text = await api.transcript(file_name)
        await message.answer(markup_text.format(text['text']), reply_markup=end_keyboard())
    else:
        if message.text == 'Хватит':
            await message.answer('Закончили', reply_markup=ReplyKeyboardRemove())
            await state.clear()
        else:
            await message.answer('Пришли голсоовое сообщение', reply_markup=end_keyboard())


@router.message(StateFilter(None))
async def uncertainty_handler(message: types.Message) -> None:
    await message.answer(
        "Такой опции нет.\n"
        "Выбери нужную функцию"
    )


def setup_voice_to_text_handler(dp):
    dp.include_router(router)
