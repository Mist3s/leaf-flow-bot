import asyncio
import logging

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.methods import TelegramMethod
from aiogram.methods.base import TelegramType

logger = logging.getLogger(__name__)


class RetryAiohttpSession(AiohttpSession):
    """
    Сессия aiogram с retry логикой для сетевых ошибок.
    
    При TelegramNetworkError повторяет запрос с экспоненциальной задержкой.
    """

    def __init__(
        self,
        *,
        timeout: float = 30.0,
        proxy: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
    ):
        super().__init__(proxy=proxy, timeout=timeout)
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def make_request(
        self,
        bot: Bot,
        method: TelegramMethod[TelegramType],
        timeout: int | None = None,
    ) -> TelegramType:
        """Выполняет запрос с retry при сетевых ошибках."""
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                return await super().make_request(bot, method, timeout)
            except TelegramNetworkError as e:
                last_error = e
                
                if attempt < self.max_retries:
                    # Экспоненциальная задержка: 1s, 2s, 4s, ...
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    logger.warning(
                        f"Telegram API network error (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Telegram API network error after {self.max_retries + 1} attempts: {e}"
                    )

        # Если все попытки исчерпаны
        raise last_error  # type: ignore[misc]
