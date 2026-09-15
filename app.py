import asyncio
import contextlib
import logging

import uvicorn
from fastapi import FastAPI

from config import PORT
import database as db
from bot import main as bot_main

logging.basicConfig(level=logging.INFO)

app = FastAPI()
_bot_task: asyncio.Task | None = None


@app.on_event("startup")
async def startup():
    global _bot_task
    await db.init_db()
    _bot_task = asyncio.create_task(bot_main())


@app.on_event("shutdown")
async def shutdown():
    if _bot_task:
        _bot_task.cancel()
        with contextlib.suppress(Exception):
            await _bot_task


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"status": "ok", "service": "mp4-webm-bot"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=False)
