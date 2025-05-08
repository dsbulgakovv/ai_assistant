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

markup_text = "**Ответ:**\n{}"

router = Router()
api = VoiceToTextAPI()


class LLMchat(StatesGroup):
    answer_questions = State()


# def get_answer_from_llm(text):
#     client = OpenAI(base_url="http://172.17.0.1:1234/v1", api_key="lm-studio")
#     completion = client.chat.completions.create(
#         model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
#         messages=[
#             {"role": "system",
#              "content": "Ты должна отвечать на вопросы пользователя на русском языке."},
#             {"role": "user",
#              "content": text}
#         ],
#         temperature=0.7,
#     )
#     answer = completion.choices[0].message.content
#
#     return answer
#
#
# @router.message(F.text.casefold() == 'задать вопрос')
# async def q_and_a_start_handler(message: types.Message, state: FSMContext) -> None:
#     await message.answer(
#         "Задай вопрос голосом или напиши текстом, а я постараюсь ответить.",
#         reply_markup=end_keyboard()
#     )
#     await state.set_state(LLMchat.answer_questions)
#
#
# @router.message(StateFilter(LLMchat.answer_questions))
# async def q_and_a_process_handler(message: types.Message, bot: Bot, state: FSMContext) -> None:
#     if message.voice:
#         file_id = message.voice.file_id
#         file = await bot.get_file(file_id)
#         file_path = file.file_path
#         file_name = f"service_files/audio_{file_id}.mp3"
#         await bot.download_file(file_path, file_name)
#         logger.info(os.listdir('./service_files'))
#         text = await api.transcript(file_name)
#         await message.answer('Голос обработан! Думаю...', reply_markup=end_keyboard())
#         answer = get_answer_from_llm(text['text'])
#         if len(answer) > 4080:
#             for x in range(0, len(answer), 4080):
#                 await message.answer(markup_text.format(answer)[x:x + 4095], reply_markup=end_keyboard())
#         else:
#             await message.answer(markup_text.format(answer), reply_markup=end_keyboard())
#     elif message.text == 'Хватит':
#         await message.answer('Закончили', reply_markup=ReplyKeyboardRemove())
#         await state.clear()
#     elif message.text:
#         await message.answer('Думаю...', reply_markup=end_keyboard())
#         answer = get_answer_from_llm(message.text)
#         if len(answer) > 4080:
#             for x in range(0, len(answer), 4080):
#                 await message.answer(markup_text.format(answer)[x:x + 4095], reply_markup=end_keyboard())
#         else:
#             await message.answer(markup_text.format(answer), reply_markup=end_keyboard())
#     else:
#         await message.answer('Задай вопрос голосом или текстом.', reply_markup=end_keyboard())


@router.message(StateFilter(None))
async def uncertainty_handler(message: types.Message) -> None:
    await message.answer(
        "Такой опции нет.\n"
        "Выбери нужную функцию"
    )
