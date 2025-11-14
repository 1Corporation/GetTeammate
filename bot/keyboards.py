from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def moderation_kb(profile_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"mod:approve:{profile_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"mod:reject:{profile_id}"),
            ]
        ]
    )
    return kb

def browse_kb(index: int, total: int, profile_id: int) -> InlineKeyboardMarkup:
    buttons = []
    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"browse:prev:{index-1}"))
    buttons.append(InlineKeyboardButton(text=f"{index+1}/{total}", callback_data="noop"))
    if index < total - 1:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"browse:next:{index+1}"))
    buttons.append(InlineKeyboardButton(text="⚠️ Пожаловаться", callback_data=f"browse:report:{profile_id}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])
