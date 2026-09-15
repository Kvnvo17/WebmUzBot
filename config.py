import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0") or 0)
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot.db")
PORT = int(os.getenv("PORT", "8000"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylida ko'rsatilmagan!")
if not ADMIN_ID:
    raise RuntimeError("ADMIN_ID .env faylida ko'rsatilmagan!")
