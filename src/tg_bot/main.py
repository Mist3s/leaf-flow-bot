import asyncio
import logging
import signal
from typing import Any

import uvicorn
from aiogram import Bot, Dispatcher

from tg_bot.bot.app import create_bot_and_dispatcher
from tg_bot.config import Settings, load_settings
from tg_bot.http_app.app import create_app
from tg_bot.logging import configure_logging

logger = logging.getLogger(__name__)


async def _run_polling(bot: Bot, dispatcher: Dispatcher) -> None:
    """Запуск бота в polling-режиме (через прокси, если настроена)."""
    logger.info("Запуск бота в polling-режиме")
    try:
        # Удаляем webhook, чтобы Telegram отдавал обновления через getUpdates
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook удалён, запускаем polling")

        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


async def _run_webhook(
    settings: Settings, bot: Bot, dispatcher: Dispatcher
) -> None:
    """Запуск бота через webhook (текущее поведение)."""
    logger.info("Запуск бота в webhook-режиме")
    app = create_app(settings=settings, bot=bot, dispatcher=dispatcher)

    config = uvicorn.Config(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
    server = uvicorn.Server(config)

    shutdown_event = asyncio.Event()

    def signal_handler() -> None:
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    serve_task = asyncio.create_task(server.serve())

    try:
        await shutdown_event.wait()
        await server.shutdown()
        try:
            await serve_task
        except asyncio.CancelledError:
            pass
    finally:
        if not serve_task.done():
            serve_task.cancel()
            try:
                await serve_task
            except asyncio.CancelledError:
                pass
        await bot.session.close()


async def _run() -> None:
    settings = load_settings()
    configure_logging(level=settings.log_level)

    bot, dispatcher = create_bot_and_dispatcher(settings)

    if settings.use_polling:
        await _run_polling(bot, dispatcher)
    else:
        await _run_webhook(settings, bot, dispatcher)


def run() -> Any:
    """Synchronous entry point for launch via `python -m tg_bot.main`."""
    return asyncio.run(_run())


if __name__ == "__main__":
    run()
