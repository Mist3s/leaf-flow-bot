from __future__ import annotations

from aiogram import Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from tg_bot.config import Settings
from tg_bot.infrastructure.mapping_store import MappingStore, ReplyTarget


class ChatService:
    def __init__(self, *, bot: Bot, settings: Settings, mapping_store: MappingStore):
        self.bot = bot
        self.settings = settings
        self.mapping_store = mapping_store

    async def handle_reply_callback(self, callback: CallbackQuery) -> None:
        data_parts = (callback.data or "").split(":", maxsplit=2)
        if len(data_parts) < 3:
            await callback.answer("Некорректные данные")
            return
        _, user_id, order_id = data_parts
        order_part = f" по заказу №{order_id}" if order_id != "none" else ""
        service_message = await self.bot.send_message(
            chat_id=self.settings.admin_chat_id,
            text=(
                f"Отвечаете пользователю @{callback.from_user.username if callback.from_user else ''}{order_part}.\n"
                "Ответьте на это сообщение любым форматом."
            ),
        )
        target = ReplyTarget(user_telegram_id=int(user_id), order_id=None if order_id == "none" else order_id)
        self.mapping_store.set_mapping(service_message.message_id, target)
        await callback.answer("Отправьте ответ пользователю в ответ на сообщение")

    async def maybe_forward_admin_reply(self, message: Message) -> bool:
        if message.chat.id != self.settings.admin_chat_id:
            return False
        if not message.reply_to_message:
            return False
        target = self.mapping_store.get_target(message.reply_to_message.message_id)
        if not target:
            return False
        await self.bot.copy_message(
            chat_id=target.user_telegram_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )
        return True
