from __future__ import annotations

import asyncio

import httpx

from tg_bot.config import load_settings


async def main() -> None:
    settings = load_settings()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://api.telegram.org/bot{settings.bot_token}/setWebhook",
            json={"url": settings.webhook_url},
        )
        resp.raise_for_status()
        result = resp.json()
        print(f"Webhook URL: {settings.webhook_url}")
        print(f"Response: {result}")
        if result.get("ok"):
            print("✅ Webhook успешно установлен!")
        else:
            print(f"❌ Ошибка установки webhook: {result.get('description')}")


if __name__ == "__main__":
    asyncio.run(main())
