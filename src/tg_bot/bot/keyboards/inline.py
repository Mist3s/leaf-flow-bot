from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


def order_actions(order_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подробнее", callback_data=f"order:{order_id}")],
            [InlineKeyboardButton(text="Чат по заказу", callback_data=f"chat:order:{order_id}")],
        ]
    )


def open_webapp_button(webapp_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Открыть приложение", web_app=WebAppInfo(url=webapp_url))]])


def orders_pagination_keyboard(next_offset: int) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой пагинации для списка заказов"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Показать еще", callback_data=f"orders:page:{next_offset}")]
        ]
    )


def admin_order_details_button(order_id: str) -> InlineKeyboardMarkup:
    """Клавиатура с кнопками для администратора"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Подробнее", callback_data=f"admin:order:{order_id}")],
            [InlineKeyboardButton(text="✏️ Изменить статус", callback_data=f"admin:status:{order_id}")]
        ]
    )


def admin_order_status_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Клавиатура для выбора статуса заказа администратором"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🆕 Создан", callback_data=f"admin:status:select:{order_id}:created"),
                InlineKeyboardButton(text="⏳ В обработке", callback_data=f"admin:status:select:{order_id}:processing")
            ],
            [
                InlineKeyboardButton(text="✅ Оплачен", callback_data=f"admin:status:select:{order_id}:paid"),
                InlineKeyboardButton(text="🎉 Выполнен", callback_data=f"admin:status:select:{order_id}:fulfilled")
            ],
            [
                InlineKeyboardButton(text="❌ Отменён", callback_data=f"admin:status:select:{order_id}:cancelled")
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"admin:status:cancel:{order_id}")]
        ]
    )


def admin_status_comment_keyboard(order_id: str, new_status: str) -> InlineKeyboardMarkup:
    """Клавиатура для ввода комментария при изменении статуса"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏭️ Пропустить комментарий", callback_data=f"admin:status:confirm:{order_id}:{new_status}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"admin:status:cancel:{order_id}")]
        ]
    )
