from __future__ import annotations

import logging
from typing import Any, Optional

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tg_bot.bot.keyboards.inline import order_actions
from tg_bot.config import Settings
from tg_bot.infrastructure.mapping_store import MappingStore, ReplyTarget
from tg_bot.services.support_topics_service import SupportTopicsService
from tg_bot.api_client.users import UsersApi


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


async def notify_order_status_update(
    *, 
    bot: Bot, 
    settings: Settings, 
    payload: dict[str, Any],
    support_topics_service: SupportTopicsService | None = None,
    users_api: UsersApi | None = None,
) -> None:
    order_id = payload.get("orderId")
    user_telegram_id = payload.get("userTelegramId")
    new_status = payload.get("newStatus")
    comment = payload.get("comment")

    if not order_id or not user_telegram_id:
        return

    status_text = _human_status(new_status)

    status_emoji = _status_emoji_emoji(new_status)
    
    if status_text == "Создан":
        lines = [
            f"✅ <b>Заказ #{order_id} создан</b>\n",
            "В ближайшее время с вами свяжется оператор. Если у вас возникнут вопросы, вы можете написать нам, нажав соответствующую кнопку ниже."
        ]
        
        # Уведомляем администратора о новом заказе
        if support_topics_service:
            try:
                # Получаем имя пользователя
                user_fullname = None
                if users_api:
                    try:
                        user_profile = await users_api.get_by_telegram(user_telegram_id)
                        if user_profile:
                            user_fullname = user_profile.full_name()
                    except Exception as e:
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Не удалось получить профиль пользователя {user_telegram_id}: {e}")
                
                await support_topics_service.notify_admin_about_new_order(
                    user_telegram_id=user_telegram_id,
                    user_fullname=user_fullname,
                    order_id=order_id,
                )
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Ошибка при отправке уведомления администратору о новом заказе: {e}", exc_info=True)

    else:
        lines = [
            f"🔔 <b>Обновление по заказу #{order_id}</b>\n",
            f"{status_emoji} <b>Новый статус:</b> {status_text}"
        ]

    if comment:
        lines.append("")
        lines.append(f"💬 <b>Комментарий:</b>\n{comment}")

    await bot.send_message(
        chat_id=user_telegram_id,
        text="\n".join(lines),
        reply_markup = order_actions(order_id)
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


def _status_emoji_emoji(status: str | None) -> str:
    """Возвращает эмодзи для статуса заказа"""
    mapping = {
        "created": "🆕",
        "processing": "⏳",
        "paid": "✅",
        "fulfilled": "🎉",
        "cancelled": "❌",
        "shipped": "🚚",
    }
    return mapping.get(status or "", "📋")


def _build_header(*, telegram_id: int, username: str | None, user_fullname: str, order_id: Optional[str]) -> str:
    header_lines = []
    if order_id:
        header_lines.append(f"📦 <b>Заказ #{order_id}</b>")
    else:
        header_lines.append("💬 <b>Обращение без заказа</b>")
    header_lines.append("")
    username_part = f"@{username}" if username else "без username"
    header_lines.append(f"👤 <b>Пользователь:</b> {user_fullname}")
    header_lines.append(f"   {username_part} | ID: {telegram_id}")
    return "\n".join(header_lines)
