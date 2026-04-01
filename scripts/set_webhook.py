import asyncio
import os

import httpx

from tg_bot.config import load_settings


async def main() -> None:
    settings = load_settings()
    proxy = os.environ.get("HTTPS_PROXY", os.environ.get("https_proxy"))
    async with httpx.AsyncClient(proxy=proxy) as client:
        print(settings.telegram_bot_token)
        resp = await client.post(
            f"https://api.telegram.org/bot{settings.telegram_bot_token}/setWebhook",
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
