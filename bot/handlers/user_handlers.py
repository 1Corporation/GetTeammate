from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F

from bot.models import ProfileCreate, ProfileDB
from bot.repository import ProfilesRepository
from bot.keyboards import browse_kb, moderation_kb
from bot.utils import notify_admins_about_new_profile
from bot.config import settings


class CreateProfileSG(StatesGroup):
    waiting_photo = State()
    waiting_description = State()

class DeleteProfileSG(StatesGroup):
    waiting_answer = State()


def register_user_handlers(dp: Dispatcher, bot: Bot):
    dp.message.register(cmd_start, Command(commands=["start", "help"]))
    dp.message.register(cmd_create_profile, Command(commands=["create"]))
    dp.message.register(process_photo, F.photo, CreateProfileSG.waiting_photo)
    dp.message.register(process_description, CreateProfileSG.waiting_description)
    dp.message.register(cmd_browse, Command(commands=["browse"]))
    dp.callback_query.register(browse_callback, lambda c: c.data and c.data.startswith("browse:"))


async def cmd_start(message: Message):
    print(message.chat.id)
    await message.reply("👋 Привет! Я бот который поможет выбрать тебе сокомандника!\n/create — создать анкету\n/browse — посмотреть подборку")


async def cmd_create_profile(message: Message, state: FSMContext):
    await message.reply("Для того чтобы твоя анкета выглядела живой и яркой, отправь какую нибудь картинку которую будут видеть другие участники!")
    await state.clear()
    await state.set_state(CreateProfileSG.waiting_photo)


async def process_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]  # best quality
    await state.update_data(photo_file_id=photo.file_id)
    await message.reply("Отлично. Теперь расскажи о себе. Это отобразится в твоей анкете")
    await state.set_state(CreateProfileSG.waiting_description)


async def process_description(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    photo_file_id = data.get("photo_file_id")
    text = message.text.strip()
    if not text:
        await message.reply("Описание пустое — попробуй ещё раз.")
        return
    profile_create = ProfileCreate(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip() or None,
        photo_file_id=photo_file_id,
        description=text,
    )
    profile_id = await ProfilesRepository.create(profile_create)
    profile_db = await ProfilesRepository.get_by_id(profile_id)
    await message.reply("Анкета отправлена на модерацию. Как только админ одобрит — она появится в подборке.")
    # notify admins
    if profile_db:
        await notify_admins_about_new_profile(bot, profile_db)
    await state.clear()


async def cmd_browse(message: Message):
    profiles = await ProfilesRepository.list_approved(limit=1000)
    if not profiles:
        await message.reply("Анкет пока что нет. Ты можешь быть первым!")
        return
    # store list in FSMContext? Simpler — keep local pagination via callbacks and fetch whole list
    first = profiles[0]
    kb = browse_kb(index=0, total=len(profiles), profile_id=first.id)
    caption = _format_profile_caption(first)
    await message.reply_photo(photo=first.photo_file_id, caption=caption, reply_markup=kb, parse_mode="HTML")


def _format_profile_caption(p: ProfileDB) -> str:
    name = p.full_name or f"@{p.username}" if p.username else "Аноним"
    return f"<b>{name}</b>\n\n{p.description}"


async def browse_callback(query: CallbackQuery):
    # callback data formats:
    # browse:prev:<index>
    # browse:next:<index>
    # browse:report:<profile_id>
    await query.answer()
    data = query.data.split(":")
    action = data[1]
    payload = data[2]

    if action == "report":
        profile_id = int(payload)
        # forward to admins
        for admin in settings.ADMINS:
            await query.bot.send_message(admin,
                                         f"Пожаловались на анкету #{profile_id} от @{query.from_user.username or query.from_user.id}")
        await query.message.reply("Спасибо, мы разберёмся.")
        return

    # next/prev: payload is index
    index = int(payload)
    profiles = await ProfilesRepository.list_approved(limit=1000)
    if not profiles:
        await query.message.edit_text("Пока нет анкет.")
        return
    if index < 0 or index >= len(profiles):
        await query.answer("Нет такой страницы.", show_alert=True)
        return
    p = profiles[index]
    kb = browse_kb(index=index, total=len(profiles), profile_id=p.id)
    caption = _format_profile_caption(p)
    # edit media
    try:
        await query.message.edit_media(
            media=await query.bot.api.build_input_media_photo(p.photo_file_id, caption=caption), reply_markup=kb,
            parse_mode="HTML")
    except Exception:
        # fallback: send new message and delete old
        await query.message.delete()
        await query.message.answer_photo(photo=p.photo_file_id, caption=caption, reply_markup=kb)
