import logging
import os

from aiogram import Bot, F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from keyboards.general import start_keyboard, end_keyboard
from utils.large_lang_model_api import LLMapi
from utils.voice_to_text_api import VoiceToTextAPI


logger = logging.getLogger('aiogram')
logger.setLevel(logging.DEBUG)

markup_text = "**Ответ:**\n{}"

router = Router()
llm_api = LLMapi()
vtt_api = VoiceToTextAPI()


class LLMchat(StatesGroup):
    answer_questions = State()


@router.message(F.text.casefold() == 'задать вопрос')
async def q_and_a_start_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Задай вопрос голосом или напиши текстом, а я постараюсь ответить.",
        reply_markup=end_keyboard()
    )
    await state.set_state(LLMchat.answer_questions)


@router.message(StateFilter(LLMchat.answer_questions))
async def q_and_a_process_handler(message: types.Message, bot: Bot, state: FSMContext) -> None:
    if message.voice:
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_name = f"service_files/audio_{file_id}.mp3"
        await bot.download_file(file_path, file_name)
        logger.info(os.listdir('./service_files'))
        text = await vtt_api.transcript(file_name)
        await message.answer('Голос обработан! Думаю...', reply_markup=end_keyboard())
        answer = llm_api.answer(text['text'])
        if len(answer) > 4080:
            for x in range(0, len(answer), 4080):
                await message.answer(markup_text.format(answer)[x:x + 4095], reply_markup=end_keyboard())
        else:
            await message.answer(markup_text.format(answer), reply_markup=end_keyboard())
    elif message.text == 'Вернуться в меню':
        await message.answer('Закончили', reply_markup=ReplyKeyboardRemove())
        await state.clear()
    elif message.text:
        await message.answer('Думаю...', reply_markup=end_keyboard())
        answer = llm_api.answer(message.text)
        if len(answer) > 4080:
            for x in range(0, len(answer), 4080):
                await message.answer(markup_text.format(answer)[x:x + 4095], reply_markup=end_keyboard())
        else:
            await message.answer(markup_text.format(answer), reply_markup=end_keyboard())
    else:
        await message.answer('Задай вопрос голосом или текстом.', reply_markup=end_keyboard())


def setup_q_and_a_handlers(dp):
    dp.include_router(router)
