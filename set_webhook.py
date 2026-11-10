import asyncio
import os
import re

from aiogram import Bot


async def main():
    token = os.environ["BOT_TOKEN"]
    secret = os.environ["WEBHOOK_SECRET"]
    app_url = os.environ["APP_URL"].rstrip("/")

    if not re.fullmatch(r"[A-Za-z0-9_-]{1,256}", secret):
        raise ValueError("WEBHOOK_SECRET must be 1-256 letters, digits, underscores, or hyphens")
    if not app_url.startswith("https://"):
        raise ValueError("APP_URL must be the deployed HTTPS URL")

    async with Bot(token=token) as bot:
        await bot.set_webhook(
            url=f"{app_url}/webhook",
            secret_token=secret,
        )

    print(f"Webhook configured: {app_url}/webhook")


if __name__ == "__main__":
    asyncio.run(main())
