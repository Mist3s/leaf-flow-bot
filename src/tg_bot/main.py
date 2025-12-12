"""Entry point to run FastAPI application with aiogram."""
from __future__ import annotations

import asyncio
import signal
from typing import Any

import uvicorn

from tg_bot.bot.app import create_bot_and_dispatcher
from tg_bot.config import load_settings
from tg_bot.http_app.app import create_app
from tg_bot.logging import configure_logging


async def _run() -> None:
    settings = load_settings()
    configure_logging(level=settings.log_level)

    bot, dispatcher = create_bot_and_dispatcher(settings)
    app = create_app(settings=settings, bot=bot, dispatcher=dispatcher)

    config = uvicorn.Config(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
    server = uvicorn.Server(config)

    async def shutdown() -> None:
        await bot.session.close()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(server.shutdown()))

    try:
        await server.serve()
    finally:
        await shutdown()


def run() -> Any:
    """Synchronous entry point for launch via `python -m tg_bot.main`."""
    return asyncio.run(_run())


if __name__ == "__main__":
    run()
