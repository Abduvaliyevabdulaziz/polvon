import hmac
import json
import os

from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import ValidationError

from bot import bot, dp


WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
app = FastAPI()


@app.get("/")
async def health_check():
    return {"status": "ok"}


@app.post("/webhook")
async def telegram_webhook(
    request: Request,
    secret_token: str | None = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
):
    if not hmac.compare_digest(secret_token or "", WEBHOOK_SECRET):
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot})
    except (json.JSONDecodeError, ValidationError):
        raise HTTPException(status_code=400, detail="Invalid Telegram update") from None

    await dp.feed_update(bot, update)
    return {"ok": True}
