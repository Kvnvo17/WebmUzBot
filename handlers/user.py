from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import database as db
from locales import t
from keyboards.user import main_menu, lang_menu, subscribe_menu

router = Router()


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    channels = await db.list_channels()
    if not channels:
        return True
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch["chat_id"], user_id=user_id)
            if member.status in ("left", "kicked"):
                return False
        except Exception:
            # Agar botni kanalga admin qilmagan bo'lsa, o'tkazib yuboramiz
            continue
    return True


async def send_start(message: Message, lang: str):
    text = await db.get_setting(f"start_{lang}") or t(lang, "WELCOME")
    await message.answer(text, reply_markup=main_menu(lang))


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    user = message.from_user
    await db.add_user(user.id, user.username or "", user.full_name or "")
    lang = await db.get_user_lang(user.id)

    if not await is_subscribed(bot, user.id):
        channels = await db.list_channels()
        await message.answer(
            t(lang, "SUB_REQUIRED"),
            reply_markup=subscribe_menu(channels, lang),
        )
        return

    await send_start(message, lang)


@router.callback_query(F.data == "sub:check")
async def sub_check(cb: CallbackQuery, bot: Bot):
    lang = await db.get_user_lang(cb.from_user.id)
    if await is_subscribed(bot, cb.from_user.id):
        await cb.message.edit_text(t(lang, "SUB_OK"))
        await send_start(cb.message, lang)
    else:
        await cb.answer(t(lang, "SUB_FAIL"), show_alert=True)


@router.message(F.text.in_({"🌐 Til", "🌐 Язык", "🌐 Language"}))
async def choose_lang(message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    await message.answer(t(lang, "LANG_CHOOSE"), reply_markup=lang_menu())


@router.callback_query(F.data.startswith("lang:"))
async def set_lang(cb: CallbackQuery):
    lang = cb.data.split(":")[1]
    await db.set_user_lang(cb.from_user.id, lang)
    await cb.message.edit_text(t(lang, "LANG_SET"))
    await cb.message.answer(t(lang, "WELCOME"), reply_markup=main_menu(lang))


@router.message(F.text.in_({"📖 Qo‘llanma", "📖 Инструкция", "📖 Guide"}))
async def guide(message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    await message.answer(t(lang, "GUIDE"))
