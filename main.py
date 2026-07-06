import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

from config import BOT_TOKEN, WEBHOOK_HOST, WEBHOOK_PORT
from database import init_db
from payment.webhook import register_click_routes
from handlers import student, admin

logging.basicConfig(level=logging.INFO)


async def start_webhook_server(bot: Bot):
    app = web.Application()
    register_click_routes(app, bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBHOOK_HOST, WEBHOOK_PORT)
    await site.start()
    logging.info(f"Click webhook server {WEBHOOK_HOST}:{WEBHOOK_PORT} portida ishga tushdi")


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(admin.router)
    dp.include_router(student.router)

    await start_webhook_server(bot)

    logging.info("Bot polling boshlandi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
