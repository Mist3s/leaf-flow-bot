from __future__ import annotations

from typing import Any, Optional

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tg_bot.config import Settings
from tg_bot.infrastructure.mapping_store import MappingStore, ReplyTarget


async def send_support_message_to_admin(
    *,
    bot: Bot,
    settings: Settings,
    mapping_store: MappingStore,
    user_fullname: str,
    username: str | None,
    telegram_id: int,
    order_id: str | None,
    source_chat_id: int,
    source_message_id: int,
) -> None:
    header = _build_header(telegram_id=telegram_id, username=username, user_fullname=user_fullname, order_id=order_id)
    reply_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Ответить пользователю", callback_data=f"reply:{telegram_id}:{order_id or 'none'}")]
        ]
    )

    header_message = await bot.send_message(chat_id=settings.admin_chat_id, text=header, reply_markup=reply_button)
    target = ReplyTarget(user_telegram_id=telegram_id, order_id=order_id)
    mapping_store.set_mapping(header_message.message_id, target)
    
    # Копируем сообщение пользователя как ответ на header_message
    copied_message = await bot.copy_message(
        chat_id=settings.admin_chat_id,
        from_chat_id=source_chat_id,
        message_id=source_message_id,
        reply_to_message_id=header_message.message_id,
    )
    # Сохраняем маппинг также для скопированного сообщения, чтобы можно было отвечать на него напрямую
    if copied_message:
        mapping_store.set_mapping(copied_message.message_id, target)


async def notify_order_status_update(*, bot: Bot, settings: Settings, payload: dict[str, Any]) -> None:
    order_id = payload.get("orderId")
    user_telegram_id = payload.get("userTelegramId")
    new_status = payload.get("newStatus")
    comment = payload.get("comment")

    if not order_id or not user_telegram_id:
        return

    status_text = _human_status(new_status)
    lines = [f"Обновление по заказу №{order_id}", f"Новый статус: {status_text}"]
    if comment:
        lines.append(str(comment))
    await bot.send_message(
        chat_id=user_telegram_id,
        text="\n".join(lines),
    )


def _human_status(status: str | None) -> str:
    mapping = {
        "created": "Создан",
        "processing": "В обработке",
        "paid": "Оплачен",
        "fulfilled": "Выполнен",
        "cancelled": "Отменён",
        "shipped": "Отправлен",
    }
    return mapping.get(status or "", status or "Неизвестно")


def _build_header(*, telegram_id: int, username: str | None, user_fullname: str, order_id: Optional[str]) -> str:
    header_lines = []
    if order_id:
        header_lines.append(f"[Заказ №{order_id}]")
    else:
        header_lines.append("[Обращение без заказа]")
    username_part = f"@{username}" if username else "без username"
    header_lines.append(f"Пользователь: {user_fullname} ({username_part} / tg_id={telegram_id})")
    return "\n".join(header_lines)
