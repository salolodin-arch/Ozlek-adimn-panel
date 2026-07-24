"""
Railway shu faylni ishga tushiradi (start command: python main.py).
Bir vaqtning o'zida uchtasi ishlaydi va bitta bazani (Volume orqali) baham ko'radi:
  - Admin bot (polling)
  - Mijozlar boti (polling)
  - JSON API (website uchun, aiohttp)
"""

import asyncio
import logging

from aiohttp import web

from admin_bot import run_admin_bot
from public_bot import run_public_bot_no_sync
from api import create_app
from config import PORT

logging.basicConfig(level=logging.INFO)


async def run_api():
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logging.info(f"API {PORT}-portda ishga tushdi")
    while True:
        await asyncio.sleep(3600)


async def main():
    await asyncio.gather(
        run_admin_bot(),
        run_public_bot_no_sync(),
        run_api(),
    )


if __name__ == "__main__":
    asyncio.run(main())
