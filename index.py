from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import hmac
import json
import os

from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import ValidationError

from bot import bot, dp


WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    if os.getenv("VERCEL_ENV") == "production":
        production_url = os.environ.get("VERCEL_PROJECT_PRODUCTION_URL")
        if not production_url:
            raise RuntimeError("VERCEL_PROJECT_PRODUCTION_URL is required in production")
        if not WEBHOOK_SECRET:
            raise RuntimeError("WEBHOOK_SECRET is required in production")
        await bot.set_webhook(
            url=f"https://{production_url}/webhook",
            secret_token=WEBHOOK_SECRET,
        )
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def health_check():
    return {"status": "ok"}


@app.post("/webhook")
async def telegram_webhook(
    request: Request,
    secret_token: str | None = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
):
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Webhook secret is not configured")
    if not hmac.compare_digest(secret_token or "", WEBHOOK_SECRET):
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot})
    except (json.JSONDecodeError, ValidationError):
        raise HTTPException(status_code=400, detail="Invalid Telegram update") from None

    await dp.feed_update(bot, update)
    return {"ok": True}
