from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Request
from aiogram import Bot

from tg_bot.infrastructure.admin_chat import notify_order_status_update
from tg_bot.infrastructure.security import verify_internal_token

router = APIRouter()


def _get_bot(request: Request) -> Bot:
    return request.app.state.bot


@router.post("/order-status-changed")
async def order_status_changed(
    payload: dict,
    request: Request,
    authorization: str | None = Header(default=None, convert_underscores=False),
    bot: Bot = Depends(_get_bot),
):
    verify_internal_token(authorization=authorization, expected_token=request.app.state.settings.internal_leafflow_token)
    await notify_order_status_update(bot=bot, settings=request.app.state.settings, payload=payload)
    return {"status": "delivered"}
