from __future__ import annotations

import logging

from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):  # type: ignore[override]
        logger.info("Incoming message", extra={"from": event.from_user.id if event.from_user else None})
        return await handler(event, data)
