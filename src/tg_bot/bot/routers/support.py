from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("support"))
@router.message(F.text == "👨‍💻 Поддержка")
async def support_entry(message: Message):
    """Информационное сообщение о поддержке через топики"""
    await message.answer(
        "Просто напишите ваш вопрос, и мы передадим его оператору. "
        "Ответы приходят автоматически в этот чат."
    )
