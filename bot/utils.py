from aiogram import Bot
from bot.models import ProfileDB
from bot.repository import ProfilesRepository
from bot.config import settings
import logging

logger = logging.getLogger(__name__)

async def notify_admins_about_new_profile(bot: Bot, profile: ProfileDB):
    for admin_id in settings.ADMINS:
        try:
            text = f"Новая анкета #{profile.id}\nОт: @{profile.username or ''} {profile.full_name or ''}\nОписание: {profile.description[:200]}"
            await bot.send_photo(chat_id=admin_id, photo=profile.photo_file_id, caption=text)
        except Exception as e:
            logger.exception("Failed to notify admin %s: %s", admin_id, e)
