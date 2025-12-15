from __future__ import annotations

from pathlib import Path

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

router = Router()


@router.message(Command("help"))
async def help_command(message: Message):
    tg_bot_dir = Path(__file__).resolve().parents[2]
    img_path = tg_bot_dir / "data" / "img" / "help_6x4.png"
    await message.answer_photo(
        photo=FSInputFile(img_path),
        caption=(
            "Я помогу отслеживать заказы и быстро связаться с оператором.\n\n"
            "Доступные команды:\n"
            "📦 /orders — мои заказы\n"
            "👨‍💻 /support — поддержка\n"
            "🛒 Открыть приложение — каталог и оформление заказа\n\n"
            "Если остались вопросы — напишите сюда, мы ответим как можно скорее."
        ),
    )
