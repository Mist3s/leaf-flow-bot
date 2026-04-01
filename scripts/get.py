import asyncio
import os
import httpx
from tg_bot.config import load_settings


async def main():
    s = load_settings()
    proxy = os.environ.get("HTTPS_PROXY", os.environ.get("https_proxy"))
    async with httpx.AsyncClient(proxy=proxy) as c:
        r = await c.get(f"https://api.telegram.org/bot{s.telegram_bot_token}/getWebhookInfo")
        r.raise_for_status()
        print(r.json())

asyncio.run(main())