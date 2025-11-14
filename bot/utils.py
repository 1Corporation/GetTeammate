import logging

from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from bot.config import settings
from bot.models import ProfileDB

logger = logging.getLogger(__name__)

async def notify_admins_about_new_profile(bot: Bot, profile: ProfileDB):
    for admin_id in settings.ADMINS:
        try:
            text = f"Новая анкета #{profile.id}\nОт: @{profile.username or ''} {profile.full_name or ''}\nОписание: {profile.description[:200]}"

            reply_markup = InlineKeyboardBuilder()
            reply_markup.row(
                InlineKeyboardButton(text="Одобрить ✅", callback_data=f"mod:approve:{profile.id}"),
                InlineKeyboardButton(text="Отклонить ❌", callback_data=f"mod:reject:{profile.id}"))
            await bot.send_photo(chat_id=admin_id, photo=profile.photo_file_id, caption=text, reply_markup=reply_markup.as_markup())

        except Exception as e:
            logger.exception("Failed to notify admin %s: %s", admin_id, e)
