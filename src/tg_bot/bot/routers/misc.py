from __future__ import annotations

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Я помогаю отслеживать ваши заказы и связываться с оператором.\n\n"
        "Доступные действия:\n"
        "• /orders — посмотреть заказы\n"
        "• Поддержка — задать любой вопрос\n"
        "• Открыть приложение — каталог товаров и оформление заказа"
    )
