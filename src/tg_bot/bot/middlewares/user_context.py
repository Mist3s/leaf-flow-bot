from __future__ import annotations

from aiogram import BaseMiddleware
from aiogram.types import Message

from tg_bot.api_client.users import UsersApi
from tg_bot.api_client.models import UserProfile


class UserContextMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):  # type: ignore[override]
        users_api: UsersApi = data.get("users_api")
        user: UserProfile | None = None
        if event.from_user and users_api:
            user = await users_api.get_by_telegram(event.from_user.id)
        data["user_profile"] = user
        return await handler(event, data)
