import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN", "")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

if not ADMIN_BOT_TOKEN or not ADMIN_CHAT_ID:
    print("OGOHLANTIRISH: .env (yoki Railway Variables) da ADMIN_BOT_TOKEN / ADMIN_CHAT_ID to'liq emas!")
