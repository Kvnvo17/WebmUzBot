import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import ADMIN_ID
from keyboards.admin import (
    admin_menu, admins_menu, subs_menu, log_menu, start_menu, ads_lang_menu,
)

router = Router()


class AdminState(StatesGroup):
    admin_add = State()
    admin_del = State()
    sub_add = State()
    sub_del = State()
    log_add = State()
    start_edit = State()
    ad_content = State()


async def is_admin(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True
    admins = await db.list_admins()
    return user_id in admins


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not await is_admin(message.from_user.id):
        return
    await message.answer("🛠 Admin panel", reply_markup=admin_menu())


@router.callback_query(F.data == "adm:close")
async def close_adm(cb: CallbackQuery):
    try:
        await cb.message.delete()
    except Exception:
        pass


@router.callback_query(F.data == "adm:back")
async def back_adm(cb: CallbackQuery):
    await cb.message.edit_text("🛠 Admin panel", reply_markup=admin_menu())


# ---------- ADMINLAR ----------

@router.callback_query(F.data == "adm:admins")
async def admins(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        return
    await cb.message.edit_text("👤 Adminlar", reply_markup=admins_menu())


@router.callback_query(F.data == "adm:admin_add")
async def admin_add(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id):
        return
    await state.set_state(AdminState.admin_add)
    await cb.message.edit_text("Yangi admin Telegram ID sini yuboring:")


@router.message(AdminState.admin_add)
async def admin_add_save(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    try:
        uid = int(message.text.strip())
    except Exception:
        await message.answer("❌ Noto‘g‘ri ID.")
        return
    await db.add_admin(uid)
    await state.clear()
    await message.answer(f"✅ Admin qo‘shildi: {uid}", reply_markup=admin_menu())


@router.callback_query(F.data == "adm:admin_del")
async def admin_del(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id):
        return
    admins = await db.list_admins()
    txt = "Adminlar:\n" + "\n".join(str(a) for a in admins) if admins else "Adminlar yo‘q."
    await state.set_state(AdminState.admin_del)
    await cb.message.edit_text(txt + "\n\nO‘chirmoqchi bo‘lgan admin ID sini yuboring:")


@router.message(AdminState.admin_del)
async def admin_del_save(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    try:
        uid = int(message.text.strip())
    except Exception:
        await message.answer("❌ Noto‘g‘ri ID.")
        return
    if uid == ADMIN_ID:
        await message.answer("❌ Asosiy adminni o‘chirib bo‘lmaydi.")
        return
    await db.remove_admin(uid)
    await state.clear()
    await message.answer(f"🗑 Admin o‘chirildi: {uid}", reply_markup=admin_menu())


# ---------- OBUNA ----------

@router.callback_query(F.data == "adm:subs")
async def subs(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        return
    await cb.message.edit_text("📋 Majburiy obuna", reply_markup=subs_menu())


@router.callback_query(F.data == "adm:sub_add")
async def sub_add(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id):
        return
    await state.set_state(AdminState.sub_add)
    await cb.message.edit_text(
        "Kanalni yuboring:\n"
        "Format: @username | Kanal nomi\n"
        "yoki: -1001234567890 | Kanal nomi"
    )


@router.message(AdminState.sub_add)
async def sub_add_save(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    parts = [p.strip() for p in (message.text or "").split("|")]
    if len(parts) != 2:
        await message.answer("❌ Format: @username | Nomi")
        return
    await db.add_channel(parts[0], parts[1])
    await state.clear()
    await message.answer("✅ Kanal qo‘shildi.", reply_markup=admin_menu())


@router.callback_query(F.data == "adm:sub_del")
async def sub_del(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id):
        return
    chs = await db.list_channels()
    if not chs:
        await cb.message.edit_text("Kanallar yo‘q.", reply_markup=subs_menu())
        return
    txt = "\n".join(f"{c['id']}. {c['title']} ({c['chat_id']})" for c in chs)
    await state.set_state(AdminState.sub_del)
    await cb.message.edit_text(txt + "\n\nO‘chirish uchun ID yuboring:")


@router.message(AdminState.sub_del)
async def sub_del_save(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    try:
        cid = int(message.text.strip())
    except Exception:
        await message.answer("❌ Noto‘g‘ri ID.")
        return
    await db.remove_channel(cid)
    await state.clear()
    await message.answer("🗑 Kanal o‘chirildi.", reply_markup=admin_menu())


@router.callback_query(F.data == "adm:sub_list")
async def sub_list(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        return
    chs = await db.list_channels()
    txt = "Kanallar yo‘q."
    if chs:
        txt = "\n".join(f"{c['id']}. {c['title']} ({c['chat_id']})" for c in chs)
    await cb.message.edit_text(txt, reply_markup=subs_menu())


# ---------- LOG KANAL ----------

@router.callback_query(F.data == "adm:log")
async def log_panel(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        return
    await cb.message.edit_text("📥 Log kanal", reply_markup=log_menu())


@router.callback_query(F.data == "adm:log_add")
async def log_add(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id):
        return
    await state.set_state(AdminState.log_add)
    await cb.message.edit_text("Log kanal ID yoki @username yuboring:")


@router.message(AdminState.log_add)
async def log_add_save(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    val = (message.text or "").strip()
    await db.set_setting("log_channel", val)
    await state.clear()
    await message.answer(f"✅ Log kanal: {val}", reply_markup=admin_menu())


@router.callback_query(F.data == "adm:log_del")
async def log_del(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        return
    await db.set_setting("log_channel", "")
    await cb.message.edit_text("🗑 Log kanal o‘chirildi.", reply_markup=log_menu())


@router.callback_query(F.data == "adm:log_show")
async def log_show(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        return
    val = await db.get_setting("log_channel")
    await cb.message.edit_text(
        f"📋 Hozirgi log kanal: {val or 'Yo‘q'}", reply_markup=log_menu()
    )


# ---------- START XABARI ----------

@router.callback_query(F.data == "adm:start")
async def start_panel(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        return
    await cb.message.edit_text("📝 Start xabari", reply_markup=start_menu())


@router.callback_query(F.data.startswith("adm:start_"))
async def start_edit(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id):
        return
    lang = cb.data.split("_")[1]
    await state.set_state(AdminState.start_edit)
    await state.update_data(lang=lang)
    cur = await db.get_setting(f"start_{lang}")
    await cb.message.edit_text(
        f"Hozirgi {lang.upper()} start:\n\n{cur}\n\nYangi matnni yuboring:"
    )


@router.message(AdminState.start_edit)
async def start_edit_save(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await db.set_setting(f"start_{lang}", message.text or "")
    await state.clear()
    await message.answer("✅ Start matni yangilandi.", reply_markup=admin_menu())


# ---------- STATISTIKA ----------

@router.callback_query(F.data == "adm:stats")
async def stats(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id):
        return
    total = await db.total_users()
    today = await db.today_users()
    m2w = await db.get_stat("mp4_to_webm")
    w2m = await db.get_stat("webm_to_mp4")
    admins = await db.list_admins()
    chs = await db.list_channels()
    txt = (
        f"📊 Statistika\n\n"
        f"👥 Jami foydalanuvchilar: {total}\n"
        f"📅 Bugungi foydalanuvchilar: {today}\n"
        f"🎥 MP4 → WEBM: {m2w}\n"
        f"🔄 WEBM → MP4: {w2m}\n"
        f"👤 Adminlar soni: {len(admins) + 1}\n"
        f"📢 Majburiy kanallar: {len(chs)}"
    )
    await cb.message.edit_text(txt, reply_markup=admin_menu())


# ---------- REKLAMA ----------

@router.callback_query(F.data == "adm:ads")
async def ads(cb: CallbackQuery, state: FSMContext):
    if not await is_admin(cb.from_user.id):
        return
    await state.set_state(AdminState.ad_content)
    await cb.message.edit_text(
        "📢 Reklama xabarini yuboring (matn, rasm, video va h.k.).\n"
        "Keyin til tanlanadi."
    )


@router.message(AdminState.ad_content)
async def ads_save(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await state.update_data(
        chat_id=message.chat.id,
        message_id=message.message_id,
    )
    await message.answer("Kimga yuborilsin?", reply_markup=ads_lang_menu())


@router.callback_query(F.data.startswith("adm:ads_"))
async def ads_send(cb: CallbackQuery, state: FSMContext, bot: Bot):
    if not await is_admin(cb.from_user.id):
        return
    target = cb.data.split("_")[1]
    data = await state.get_data()
    chat_id = data.get("chat_id")
    message_id = data.get("message_id")
    if not chat_id or not message_id:
        await cb.message.edit_text("❌ Xabar topilmadi.")
        return

    if target == "all":
        users = await db.all_users()
    else:
        users = await db.users_by_lang(target)

    await cb.message.edit_text(f"⏳ Yuborilmoqda... ({len(users)})")

    ok = 0
    fail = 0
    for uid in users:
        try:
            await bot.copy_message(chat_id=uid, from_chat_id=chat_id, message_id=message_id)
            ok += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.05)

    await cb.message.answer(
        f"📢 Reklama yuborildi.\n\n"
        f"👥 Jami: {len(users)}\n"
        f"✅ Muvaffaqiyatli: {ok}\n"
        f"🚫 Bloklagan: {fail}",
        reply_markup=admin_menu(),
    )
    await state.clear()
