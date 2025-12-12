from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from tg_bot.api_client.orders import OrdersApi
from tg_bot.api_client.users import UsersApi
from tg_bot.bot.keyboards.inline import order_actions, open_webapp_button
from tg_bot.config import Settings
from tg_bot.services.order_service import OrdersTextBuilder

router = Router()


@router.message(Command("orders"))
@router.message(F.text == "📦 Мои заказы")
async def list_orders(message: Message, settings: Settings, users_api: UsersApi, orders_api: OrdersApi, order_builder: OrdersTextBuilder):
    user_profile = await users_api.get_by_telegram(message.from_user.id) if message.from_user else None
    if not user_profile:
        await message.answer(
            "Похоже, вы ещё не заходили в приложение. Нажмите кнопку, чтобы открыть его.",
            reply_markup=open_webapp_button(str(settings.webapp_url)),
        )
        return

    orders = await orders_api.list_orders(user_profile.telegramId)
    if not orders.items:
        await message.answer(
            "У вас пока нет заказов.\n\nВы можете оформить первый заказ через наше приложение.",
            reply_markup=open_webapp_button(str(settings.webapp_url)),
        )
        return

    for order in orders.items:
        await message.answer(order_builder._format_order(order), reply_markup=order_actions(order.orderId))


@router.callback_query(lambda c: c.data and c.data.startswith("order:"))
async def order_details(callback: CallbackQuery, orders_api: OrdersApi, order_builder: OrdersTextBuilder):
    order_id = callback.data.split(":", maxsplit=1)[1]
    details = await orders_api.get_order(order_id)
    await callback.message.answer(order_builder.order_details(details))
    await callback.answer()
