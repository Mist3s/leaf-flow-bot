from __future__ import annotations

import logging
from typing import Optional

from pydantic import BaseModel

from tg_bot.api_client.base import BaseApiClient
from tg_bot.api_client.errors import ApiClientError

logger = logging.getLogger(__name__)


class SupportTopicMapping(BaseModel):
    user_telegram_id: int
    admin_chat_id: int
    thread_id: int


class SupportTopicsApi(BaseApiClient):
    async def get_by_telegram(self, user_telegram_id: int) -> Optional[SupportTopicMapping]:
        """Получить связь по user_telegram_id"""
        try:
            logger.debug(f"Запрос связи для user_telegram_id={user_telegram_id}")
            response = await self._get(f"/api/v1/internal/support-topics/by-telegram/{user_telegram_id}")
            mapping = SupportTopicMapping.model_validate(response.json())
            logger.info(f"Найдена связь для user_telegram_id={user_telegram_id}, thread_id={mapping.thread_id}")
            return mapping
        except ApiClientError as e:
            if e.status_code == 404:
                logger.debug(f"Связь для user_telegram_id={user_telegram_id} не найдена (404)")
                return None
            logger.error(f"Ошибка API при получении связи для user_telegram_id={user_telegram_id}: {e.status_code} {e}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении связи для user_telegram_id={user_telegram_id}: {e}")
            raise

    async def get_by_thread(self, admin_chat_id: int, thread_id: int) -> Optional[SupportTopicMapping]:
        """Получить связь по thread_id"""
        try:
            logger.debug(f"Запрос связи для thread_id={thread_id}, admin_chat_id={admin_chat_id}")
            response = await self._get(
                "/api/v1/internal/support-topics/by-thread",
                params={"admin_chat_id": admin_chat_id, "thread_id": thread_id}
            )
            mapping = SupportTopicMapping.model_validate(response.json())
            logger.info(f"Найдена связь для thread_id={thread_id}, user_telegram_id={mapping.user_telegram_id}")
            return mapping
        except ApiClientError as e:
            if e.status_code == 404:
                logger.debug(f"Связь для thread_id={thread_id} не найдена (404)")
                return None
            logger.error(f"Ошибка API при получении связи для thread_id={thread_id}: {e.status_code} {e}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении связи для thread_id={thread_id}: {e}")
            raise

    async def ensure_mapping(
        self,
        user_telegram_id: int,
        admin_chat_id: int,
        thread_id: int
    ) -> SupportTopicMapping:
        """Создать/обеспечить связь (идемпотентно)"""
        try:
            logger.info(
                f"Создание/обеспечение связи: user_telegram_id={user_telegram_id}, "
                f"admin_chat_id={admin_chat_id}, thread_id={thread_id}"
            )
            response = await self._post(
                "/api/v1/internal/support-topics/ensure",
                json={
                    "user_telegram_id": user_telegram_id,
                    "admin_chat_id": admin_chat_id,
                    "thread_id": thread_id,
                },
            )
            mapping = SupportTopicMapping.model_validate(response.json())
            logger.info(
                f"Связь успешно создана/получена: user_telegram_id={mapping.user_telegram_id}, "
                f"thread_id={mapping.thread_id}"
            )
            return mapping
        except ApiClientError as e:
            logger.error(
                f"Ошибка API при создании связи: user_telegram_id={user_telegram_id}, "
                f"thread_id={thread_id}, status={e.status_code}, error={e}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Неожиданная ошибка при создании связи: user_telegram_id={user_telegram_id}, "
                f"thread_id={thread_id}, error={e}"
            )
            raise

