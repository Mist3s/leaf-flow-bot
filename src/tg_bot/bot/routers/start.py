from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from tg_bot.bot.keyboards.reply import main_menu
from tg_bot.services.user_service import UserService
from tg_bot.api_client.orders import OrdersApi
from tg_bot.api_client.users import UsersApi
from tg_bot.config import Settings

router = Router()


@router.message(CommandStart())
async def start_command(message: Message, settings: Settings, users_api: UsersApi, orders_api: OrdersApi, user_service: UserService):
    user_profile = None
    if message.from_user:
        user_profile = await users_api.get_by_telegram(message.from_user.id)

    if not user_profile:
        text, _ = user_service.greeting_for_unknown(message.from_user.first_name if message.from_user else None)
        await message.answer(text, reply_markup=main_menu(webapp_url=str(settings.webapp_url)))
        return

    orders = await orders_api.list_orders(user_profile.telegramId)
    has_orders = len(orders.items) > 0
    text, _ = user_service.greeting_with_orders(user_profile, has_orders)
    await message.answer(text, reply_markup=main_menu(webapp_url=str(settings.webapp_url)))
