from __future__ import annotations

from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

router = Router()

@router.message(Command("support"))
@router.message(F.text == "👨‍💻 Поддержка")
async def support_entry(message: Message):
    tg_bot_dir = Path(__file__).resolve().parents[2]
    img_path = tg_bot_dir / "data" / "img" / "support_6x4.png"
    await message.answer_photo(
        photo=FSInputFile(img_path),
        caption=(
            "Напишите ваш вопрос — мы передадим его оператору.\n"
            "Ответ придёт автоматически в этот чат."
        ),
    )
