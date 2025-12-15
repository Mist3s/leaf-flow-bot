from __future__ import annotations

import logging
from typing import Optional

from tg_bot.api_client.base import BaseApiClient
from tg_bot.api_client.models import UserProfile, RegisterUserRequest
from tg_bot.api_client.errors import ApiClientError

logger = logging.getLogger(__name__)


class UsersApi(BaseApiClient):
    async def get_by_telegram(self, telegram_id: int) -> Optional[UserProfile]:
        try:
            response = await self._get(f"/api/v1/internal/users/by-telegram/{telegram_id}")
        except Exception as exc:  # noqa: BLE001
            return None
        return UserProfile.model_validate(response.json())

    async def register(self, request: RegisterUserRequest) -> UserProfile:
        """
        Зарегистрировать нового пользователя.
        
        Args:
            request: Данные пользователя для регистрации
            
        Returns:
            UserProfile: Профиль зарегистрированного пользователя
            
        Raises:
            ApiClientError: При ошибке API
        """
        try:
            logger.info(f"Регистрация пользователя с telegramId={request.telegramId}")
            response = await self._post(
                "/api/v1/internal/users/register",
                json=request.model_dump(exclude_none=True),
            )
            user_profile = UserProfile.model_validate(response.json())
            logger.info(f"Пользователь успешно зарегистрирован: id={user_profile.id}, telegramId={user_profile.telegramId}")
            return user_profile
        except ApiClientError as e:
            logger.error(f"Ошибка API при регистрации пользователя telegramId={request.telegramId}: {e.status_code} {e}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при регистрации пользователя telegramId={request.telegramId}: {e}")
            raise
