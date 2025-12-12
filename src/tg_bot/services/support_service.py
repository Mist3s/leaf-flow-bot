from __future__ import annotations

from aiogram import Bot
from aiogram.types import Message

from tg_bot.config import Settings
from tg_bot.infrastructure.admin_chat import send_support_message_to_admin
from tg_bot.infrastructure.mapping_store import MappingStore


class SupportService:
    def __init__(self, *, bot: Bot, settings: Settings, mapping_store: MappingStore):
        self.bot = bot
        self.settings = settings
        self.mapping_store = mapping_store

    async def forward_support(self, message: Message, order_id: str | None = None) -> None:
        from_user = message.from_user
        await send_support_message_to_admin(
            bot=self.bot,
            settings=self.settings,
            mapping_store=self.mapping_store,
            user_fullname=from_user.full_name if from_user else "Пользователь",
            username=from_user.username if from_user else None,
            telegram_id=from_user.id if from_user else 0,
            order_id=order_id,
            source_chat_id=message.chat.id,
            source_message_id=message.message_id,
        )
