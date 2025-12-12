from __future__ import annotations

from fastapi import APIRouter, Depends, Request, HTTPException
from aiogram import Bot, Dispatcher
from aiogram.types import Update

router = APIRouter()


def _get_bot(request: Request) -> Bot:
    return request.app.state.bot


def _get_dispatcher(request: Request) -> Dispatcher:
    return request.app.state.dispatcher


def _verify_secret(request: Request) -> None:
    secret = request.query_params.get("secret_token")
    expected = request.app.state.settings.webhook_secret
    if secret != expected:
        raise HTTPException(status_code=403, detail="invalid secret")


@router.post("/telegram/webhook")
async def handle_telegram_webhook(
    request: Request,
    bot: Bot = Depends(_get_bot),
    dispatcher: Dispatcher = Depends(_get_dispatcher),
) -> dict[str, str]:
    _verify_secret(request)
    payload = await request.json()
    update = Update.model_validate(payload)
    await dispatcher.feed_update(bot=bot, update=update)
    return {"status": "accepted"}
