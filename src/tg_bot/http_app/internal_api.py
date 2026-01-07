from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Request
from aiogram import Bot

from tg_bot.infrastructure.admin_chat import notify_order_status_update, notify_website_order
from tg_bot.infrastructure.security import verify_internal_token
from tg_bot.services.support_topics_service import SupportTopicsService
from tg_bot.api_client.users import UsersApi

router = APIRouter()


def _get_bot(request: Request) -> Bot:
    return request.app.state.bot


def _get_support_topics_service(request: Request) -> SupportTopicsService | None:
    dispatcher = request.app.state.dispatcher
    return dispatcher.get("support_topics_service")


def _get_users_api(request: Request) -> UsersApi | None:
    dispatcher = request.app.state.dispatcher
    return dispatcher.get("users_api")


@router.post("/order-status-changed")
async def order_status_changed(
    payload: dict,
    request: Request,
    authorization: str | None = Header(default=None, convert_underscores=False),
    bot: Bot = Depends(_get_bot),
    support_topics_service: SupportTopicsService | None = Depends(_get_support_topics_service),
    users_api: UsersApi | None = Depends(_get_users_api),
):
    verify_internal_token(authorization=authorization, expected_token=request.app.state.settings.internal_leafflow_token)
    await notify_order_status_update(
        bot=bot, 
        settings=request.app.state.settings, 
        payload=payload,
        support_topics_service=support_topics_service,
        users_api=users_api,
    )
    return {"status": "delivered"}


@router.post("/website-order-created")
async def website_order_created(
    payload: dict,
    request: Request,
    authorization: str | None = Header(default=None, convert_underscores=False),
    bot: Bot = Depends(_get_bot),
):
    """
    Эндпоинт для уведомлений о заказах с сайта.
    
    Заказы от пользователей без Telegram ID (только email/телефон).
    Уведомление отправляется в General топик админского чата.
    
    Ожидаемые поля в payload:
    - orderId: str (обязательно)
    - email: str (опционально)
    - phone: str (опционально)
    - customerName: str (опционально)
    - total: str (опционально)
    - deliveryMethod: str (опционально)
    - comment: str (опционально)
    """
    verify_internal_token(authorization=authorization, expected_token=request.app.state.settings.internal_leafflow_token)
    await notify_website_order(
        bot=bot,
        settings=request.app.state.settings,
        payload=payload,
    )
    return {"status": "delivered"}
