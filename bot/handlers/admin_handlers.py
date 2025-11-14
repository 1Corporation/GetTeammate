from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from bot.repository import ProfilesRepository
from bot.keyboards import moderation_kb
from bot.config import settings

def register_admin_handlers(dp: Dispatcher, bot: Bot):
    dp.message.register(cmd_pending, Command(commands=["pending"]))
    dp.callback_query.register(moderation_callback, lambda c: c.data and c.data.startswith("mod:"))

async def _is_admin(user_id: int) -> bool:
    return user_id in settings.ADMINS

async def cmd_pending(message: Message):
    if not await _is_admin(message.from_user.id):
        await message.reply("Только админы могут видеть список ожидющих.")
        return
    pending = await ProfilesRepository.list_pending()
    if not pending:
        await message.reply("Нет ожидающих анкет.")
        return
    for p in pending:
        text = f"#{p.id} От: @{p.username or ''} {p.full_name or ''}\n\n{p.description}"
        kb = moderation_kb(p.id)
        try:
            await message.reply_photo(photo=p.photo_file_id, caption=text, reply_markup=kb)
        except Exception:
            await message.reply(text, reply_markup=kb)

async def moderation_callback(query: CallbackQuery):
    # mod:approve:<id> or mod:reject:<id>
    await query.answer()
    data = query.data.split(":")
    action = data[1]
    profile_id = int(data[2])
    if not await _is_admin(query.message.chat.id):
        await query.answer("Нет прав", show_alert=True)
        return
    if action == "approve":
        await ProfilesRepository.set_status(profile_id, "approved")
        await query.message.edit_caption(caption=f"Анкета #{profile_id} — одобрено ✅", reply_markup=None)
    elif action == "reject":
        await ProfilesRepository.set_status(profile_id, "rejected")
        await query.message.edit_caption(f"Анкета #{profile_id} — отклонено ❌")
        await query.message.answer(f"Анкета #{profile_id} отклонена.")
