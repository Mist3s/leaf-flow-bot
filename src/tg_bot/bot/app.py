from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from tg_bot.bot.routers import start, orders, support, chat, misc, support_topics
from tg_bot.bot.middlewares.logging import LoggingMiddleware
from tg_bot.bot.middlewares.user_context import UserContextMiddleware
from tg_bot.config import Settings
from tg_bot.api_client.users import UsersApi
from tg_bot.api_client.orders import OrdersApi
from tg_bot.api_client.support_topics import SupportTopicsApi
from tg_bot.services.order_service import OrdersTextBuilder
from tg_bot.services.user_service import UserService
from tg_bot.services.support_topics_service import SupportTopicsService


def create_bot_and_dispatcher(settings: Settings) -> tuple[Bot, Dispatcher]:
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher = Dispatcher()

    users_api = UsersApi(base_url=str(settings.api_base_url), token=settings.internal_bot_token)
    orders_api = OrdersApi(base_url=str(settings.api_base_url), token=settings.internal_bot_token)
    support_topics_api = SupportTopicsApi(base_url=str(settings.api_base_url), token=settings.internal_bot_token)
    order_builder = OrdersTextBuilder(webapp_url=str(settings.webapp_url))
    user_service = UserService(order_builder=order_builder, webapp_url=str(settings.webapp_url))
    support_topics_service = SupportTopicsService(
        bot=bot,
        settings=settings,
        support_topics_api=support_topics_api,
    )

    dispatcher['settings'] = settings
    dispatcher['users_api'] = users_api
    dispatcher['orders_api'] = orders_api
    dispatcher['support_topics_api'] = support_topics_api
    dispatcher['order_builder'] = order_builder
    dispatcher['user_service'] = user_service
    dispatcher['support_topics_service'] = support_topics_service

    dispatcher.message.middleware(LoggingMiddleware())
    dispatcher.message.middleware(UserContextMiddleware())

    dispatcher.include_router(start.router)
    dispatcher.include_router(orders.router)
    dispatcher.include_router(support.router)
    dispatcher.include_router(chat.router)
    dispatcher.include_router(misc.router)
    # Подключаем support_topics последним, чтобы он был catch-all для личных сообщений
    dispatcher.include_router(support_topics.router)

    return bot, dispatcher
