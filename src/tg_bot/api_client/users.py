from __future__ import annotations

from typing import Optional

from tg_bot.api_client.base import BaseApiClient
from tg_bot.api_client.models import UserProfile


class UsersApi(BaseApiClient):
    async def get_by_telegram(self, telegram_id: int) -> Optional[UserProfile]:
        try:
            response = await self._get(f"/api/v1/internal/users/by-telegram/{telegram_id}")
        except Exception as exc:  # noqa: BLE001
            return None
        return UserProfile.model_validate(response.json())
