import asyncio
import logging
from aiohttp import web

from admin_bot import run_admin_bot
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
        run_api(),
    )


if __name__ == "__main__":
    asyncio.run(main())
