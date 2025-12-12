from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot.bot.states import SupportStates
from tg_bot.services.support_service import SupportService

router = Router()


@router.message(Command("support"))
@router.message(F.text == "👨‍💻 Поддержка")
async def support_entry(message: Message, state: FSMContext):
    await state.set_state(SupportStates.waiting_message)
    await message.answer(
        "Напишите ваш вопрос одним сообщением, и мы передадим его оператору.",
    )


@router.message(SupportStates.waiting_message)
async def handle_support(message: Message, state: FSMContext, support_service: SupportService):
    await support_service.forward_support(message)
    await message.answer("Ваше сообщение отправлено оператору. Обычно отвечаем в течение нескольких минут.")
    await state.clear()
