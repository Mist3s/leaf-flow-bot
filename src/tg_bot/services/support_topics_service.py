from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from tg_bot.api_client.support_topics import SupportTopicsApi
from tg_bot.config import Settings

logger = logging.getLogger(__name__)


class SupportTopicsService:
    def __init__(self, *, bot: Bot, settings: Settings, support_topics_api: SupportTopicsApi):
        self.bot = bot
        self.settings = settings
        self.support_topics_api = support_topics_api

    async def get_or_create_thread(
        self,
        user_telegram_id: int,
        user_fullname: str | None = None,
        order_id: str | None = None,
    ) -> int:
        """
        Получить thread_id для пользователя или создать новый топик.
        
        Args:
            user_telegram_id: Telegram ID пользователя
            user_fullname: Полное имя пользователя для названия топика
            order_id: Опциональный ID заказа для добавления в название топика
            
        Returns:
            thread_id топика в админской супергруппе
        """
        # Пытаемся получить существующую связь
        logger.debug(f"Попытка получить существующую связь для user_telegram_id={user_telegram_id}")
        try:
            mapping = await self.support_topics_api.get_by_telegram(user_telegram_id)
            if mapping:
                logger.info(
                    f"Используем существующий топик для user_telegram_id={user_telegram_id}, "
                    f"thread_id={mapping.thread_id}"
                )
                return mapping.thread_id
        except Exception as e:
            logger.warning(
                f"Ошибка при получении существующей связи для user_telegram_id={user_telegram_id}: {e}. "
                f"Продолжаем создание нового топика."
            )
            # Продолжаем создание нового топика, если не удалось получить связь

        # Связи нет - создаём новый топик
        topic_name = f"{user_fullname or user_telegram_id}"
        if order_id:
            topic_name = f"{topic_name} (Заказ №{order_id})"
        
        logger.info(f"Создание нового топика для user_telegram_id={user_telegram_id}, название: {topic_name}")
        try:
            forum_topic = await self.bot.create_forum_topic(
                chat_id=self.settings.admin_chat_id,
                name=topic_name,
            )
            thread_id = forum_topic.message_thread_id
            logger.info(f"Топик успешно создан: thread_id={thread_id} для user_telegram_id={user_telegram_id}")
        except Exception as e:
            logger.error(f"Ошибка при создании топика для пользователя {user_telegram_id}: {e}", exc_info=True)
            raise

        # Сохраняем связь в API
        logger.info(f"Сохранение связи в API: user_telegram_id={user_telegram_id}, thread_id={thread_id}")
        try:
            mapping = await self.support_topics_api.ensure_mapping(
                user_telegram_id=user_telegram_id,
                admin_chat_id=self.settings.admin_chat_id,
                thread_id=thread_id,
            )
            logger.info(
                f"Связь успешно сохранена в API: user_telegram_id={mapping.user_telegram_id}, "
                f"thread_id={mapping.thread_id}"
            )
        except Exception as e:
            logger.error(
                f"КРИТИЧЕСКАЯ ОШИБКА при сохранении связи для пользователя {user_telegram_id}, "
                f"thread_id={thread_id}: {e}",
                exc_info=True
            )
            # Пробрасываем исключение, чтобы не создавать топики без связи в API
            # Это предотвратит создание множества топиков при проблемах с API
            raise

        return thread_id

    async def forward_user_to_topic(self, message: Message, order_id: str | None = None) -> None:
        """
        Переслать сообщение пользователя в соответствующий топик админской супергруппы.
        
        Args:
            message: Сообщение от пользователя
            order_id: Опциональный ID заказа
        """
        if not message.from_user:
            logger.warning("Попытка переслать сообщение без from_user")
            return

        user_telegram_id = message.from_user.id
        user_fullname = message.from_user.full_name

        try:
            thread_id = await self.get_or_create_thread(
                user_telegram_id=user_telegram_id,
                user_fullname=user_fullname,
                order_id=order_id,
            )
        except Exception as e:
            logger.error(
                f"КРИТИЧЕСКАЯ ОШИБКА при получении/создании топика для пользователя {user_telegram_id}: {e}",
                exc_info=True
            )
            # Возвращаемся, чтобы не падать боту, но логируем полную информацию
            return

        try:
            await self.bot.copy_message(
                chat_id=self.settings.admin_chat_id,
                message_thread_id=thread_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )
        except Exception as e:
            logger.error(
                f"Ошибка при пересылке сообщения пользователя {user_telegram_id} "
                f"в топик {thread_id}: {e}"
            )

    async def forward_admin_to_user(self, message: Message) -> None:
        """
        Переслать сообщение админа из топика пользователю в личку.
        
        Args:
            message: Сообщение админа из топика
        """
        if not message.message_thread_id:
            logger.warning("Попытка переслать сообщение без message_thread_id")
            return

        thread_id = message.message_thread_id
        admin_chat_id = message.chat.id

        try:
            mapping = await self.support_topics_api.get_by_thread(
                admin_chat_id=admin_chat_id,
                thread_id=thread_id,
            )
        except Exception as e:
            logger.error(
                f"Ошибка при получении связи для thread_id={thread_id}, "
                f"admin_chat_id={admin_chat_id}: {e}"
            )
            return

        if not mapping:
            logger.warning(
                f"Не найдено соответствие для thread_id={thread_id}, "
                f"admin_chat_id={admin_chat_id}"
            )
            return

        user_telegram_id = mapping.user_telegram_id

        try:
            await self.bot.copy_message(
                chat_id=user_telegram_id,
                from_chat_id=admin_chat_id,
                message_id=message.message_id,
            )
        except TelegramBadRequest as e:
            # Пользователь заблокировал бота или другие проблемы с доставкой
            logger.warning(
                f"Не удалось отправить сообщение пользователю {user_telegram_id} "
                f"(возможно, бот заблокирован): {e}"
            )
        except Exception as e:
            logger.error(
                f"Ошибка при пересылке сообщения админа пользователю {user_telegram_id}: {e}"
            )

