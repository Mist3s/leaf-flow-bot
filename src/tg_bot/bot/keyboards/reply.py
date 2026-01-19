from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_with_inline_webapp(webapp_url: str) -> tuple[ReplyKeyboardMarkup, InlineKeyboardMarkup]:
    """
    Возвращает клавиатуру с обычными кнопками и отдельную инлайн-кнопку для webapp с initData.
    Инлайн-кнопка гарантирует передачу initData в webapp.
    """
    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Мои заказы"), KeyboardButton(text="👨‍💻 Поддержка")],
        ],
        resize_keyboard=True,
    )
    
    inline_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Открыть приложение", web_app=WebAppInfo(url=webapp_url))]
        ]
    )
    
    return reply_markup, inline_markup
