from __future__ import annotations

import asyncio

import httpx

from tg_bot.config import load_settings


async def main() -> None:
    settings = load_settings()
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.telegram.org/bot{settings.bot_token}/setWebhook",
            params={"url": settings.webhook_url},
        )
        print(resp.json())


if __name__ == "__main__":
    asyncio.run(main())
