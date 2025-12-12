from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher

from tg_bot.config import Settings
from tg_bot.http_app import telegram_webhook, internal_api, health


def create_app(settings: Settings, bot: Bot, dispatcher: Dispatcher) -> FastAPI:
    app = FastAPI(title="LeafFlow Telegram Bot")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.settings = settings
    app.state.bot = bot
    app.state.dispatcher = dispatcher

    app.include_router(telegram_webhook.router, prefix="", tags=["telegram"])
    app.include_router(internal_api.router, prefix="/internal", tags=["internal"])
    app.include_router(health.router, tags=["health"])

    return app
