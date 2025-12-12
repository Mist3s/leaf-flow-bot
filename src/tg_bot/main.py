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

    shutdown_event = asyncio.Event()

    async def cleanup() -> None:
        await bot.session.close()

    def signal_handler() -> None:
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    serve_task = asyncio.create_task(server.serve())
    
    try:
        # Wait for shutdown signal
        await shutdown_event.wait()
        # Properly shutdown the server and await completion
        await server.shutdown()
        # Wait for serve task to complete
        try:
            await serve_task
        except asyncio.CancelledError:
            pass
    finally:
        # Ensure serve task is cancelled if still running
        if not serve_task.done():
            serve_task.cancel()
            try:
                await serve_task
            except asyncio.CancelledError:
                pass
        await cleanup()


def run() -> Any:
    """Synchronous entry point for launch via `python -m tg_bot.main`."""
    return asyncio.run(_run())


if __name__ == "__main__":
    run()
