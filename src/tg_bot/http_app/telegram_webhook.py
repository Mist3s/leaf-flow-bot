from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks
from aiogram import Bot, Dispatcher
from aiogram.types import Update

logger = logging.getLogger(__name__)

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


async def _process_update(dispatcher: Dispatcher, bot: Bot, update: Update) -> None:
    """Обработка update в фоновой задаче с таймаутом и обработкой ошибок."""
    try:
        # Таймаут на обработку одного update — 55 секунд 
        # (меньше чем 60 сек таймаут Telegram на повторную отправку)
        async with asyncio.timeout(55.0):
            await dispatcher.feed_update(bot=bot, update=update)
    except asyncio.TimeoutError:
        logger.error(f"Timeout processing update id={update.update_id}")
    except Exception as e:
        logger.exception(f"Error processing update id={update.update_id}: {e}")


@router.post("/telegram/webhook")
async def handle_telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    bot: Bot = Depends(_get_bot),
    dispatcher: Dispatcher = Depends(_get_dispatcher),
) -> dict[str, str]:
    """
    Webhook для получения обновлений от Telegram.
    
    Обработка выполняется в фоновой задаче, чтобы:
    1. Быстро вернуть ответ Telegram (избежать таймаута)
    2. Не блокировать обработку следующих обновлений
    """
    _verify_secret(request)
    payload = await request.json()
    update = Update.model_validate(payload)
    
    # Запускаем обработку в фоне и сразу возвращаем ответ
    background_tasks.add_task(_process_update, dispatcher, bot, update)
    
    return {"status": "accepted"}
