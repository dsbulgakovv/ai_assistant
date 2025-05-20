from aiogram import Router, types
from aiogram.filters import StateFilter
from keyboards.general import start_keyboard


router = Router()


# Этот хэндлер сработает ТОЛЬКО если ни один другой хэндлер не обработал сообщение
@router.message(StateFilter(None))
async def uncertainty_handler(message: types.Message) -> None:
    await message.answer(
        "Такой опции нет.\n"
        "Выбери нужную функцию из меню ниже:",
        reply_markup=start_keyboard()  # Можно добавить клавиатуру с командами
    )


def setup_uncertainty_handlers(dp):
    dp.include_router(router)
