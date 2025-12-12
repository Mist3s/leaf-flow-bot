from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo


def main_menu(webapp_url: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Мои заказы"), KeyboardButton(text="👨‍💻 Поддержка")],
            [KeyboardButton(text="🛒 Открыть приложение", web_app=WebAppInfo(url=webapp_url))],
        ],
        resize_keyboard=True,
    )
