import asyncio
import httpx
from tg_bot.config import load_settings

async def main():
    s = load_settings()
    async with httpx.AsyncClient() as c:
        r = await c.get(f"https://api.telegram.org/bot{s.bot_token}/getWebhookInfo")
        r.raise_for_status()
        print(r.json())

asyncio.run(main())