# AI GENERATED
import logging
import asyncio

from bot.config import settings
from bot.db import Database
from bot.handlers.user_handlers import register_user_handlers
from bot.handlers.admin_handlers import register_admin_handlers
from dp import dp, bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # init DB
    await Database.init(settings.DATABASE_URL)

    # register handlers
    register_user_handlers(dp, bot)
    register_admin_handlers(dp, bot)

    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await Database.close()

if __name__ == "__main__":
    asyncio.run(main())
