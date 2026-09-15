import os
import tempfile
import uuid
from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from locales import t
from services import converter as conv
from handlers.user import is_subscribed

router = Router()


class ConvState(StatesGroup):
    wait_mp4 = State()
    wait_webm = State()


BTN_MP4 = {"🎥 MP4 → WEBM"}
BTN_WEBM = {"🔄 WEBM → MP4"}


@router.message(F.text.in_(BTN_MP4))
async def ask_mp4(message: Message, state: FSMContext, bot: Bot):
    if not await is_subscribed(bot, message.from_user.id):
        lang = await db.get_user_lang(message.from_user.id)
        await message.answer(t(lang, "SUB_REQUIRED"))
        return
    lang = await db.get_user_lang(message.from_user.id)
    await state.set_state(ConvState.wait_mp4)
    await message.answer(t(lang, "ASK_MP4"))


@router.message(F.text.in_(BTN_WEBM))
async def ask_webm(message: Message, state: FSMContext, bot: Bot):
    if not await is_subscribed(bot, message.from_user.id):
        lang = await db.get_user_lang(message.from_user.id)
        await message.answer(t(lang, "SUB_REQUIRED"))
        return
    lang = await db.get_user_lang(message.from_user.id)
    await state.set_state(ConvState.wait_webm)
    await message.answer(t(lang, "ASK_WEBM"))


async def _download(bot: Bot, file_id: str, suffix: str):
    try:
        f = await bot.get_file(file_id)
        path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}{suffix}")
        await bot.download_file(f.file_path, path)
        return path
    except Exception as e:
        print("download error:", e)
        return None


# ---------------- MP4 -> WEBM ----------------

@router.message(ConvState.wait_mp4, F.video | F.document)
async def handle_mp4(message: Message, state: FSMContext, bot: Bot):
    lang = await db.get_user_lang(message.from_user.id)

    file_id = None
    mime = ""
    fname = ""

    if message.video:
        file_id = message.video.file_id
        mime = (message.video.mime_type or "").lower()
        fname = (message.video.file_name or "").lower()
    elif message.document:
        file_id = message.document.file_id
        mime = (message.document.mime_type or "").lower()
        fname = (message.document.file_name or "").lower()

    if not file_id:
        await message.answer(t(lang, "ERR_NOT_MP4"))
        return

    is_mp4 = (
        "mp4" in mime
        or fname.endswith(".mp4")
        or fname.endswith(".m4v")
        or fname.endswith(".mov")
    )
    if not is_mp4:
        await message.answer(t(lang, "ERR_NOT_MP4"))
        return

    src = None
    dst = None
    try:
        src = await _download(bot, file_id, ".mp4")
        if not src:
            await message.answer(t(lang, "ERR_GENERIC"))
            return

        info = await conv.get_video_info(src)
        if not info:
            await message.answer(
                "❌ Videoni o‘qib bo‘lmadi.\n"
                "Fayl buzuq yoki noto‘g‘ri format."
            )
            return

        w, h, dur = info

        # O'lcham tekshiruvi (1 piksel tolerantlik)
        if abs(w - 512) > 1 or abs(h - 512) > 1:
            await message.answer(
                f"❌ Video o‘lchami 512×512 bo‘lishi kerak.\n"
                f"📐 Sizning video: {w}×{h}"
            )
            return

        # Davomiylik tekshiruvi
        if dur > 3.05:
            await message.answer(
                f"❌ Video 3 soniyadan uzun bo‘lmasligi kerak.\n"
                f"⏱ Sizning video: {dur:.2f} soniya"
            )
            return

        await message.answer(t(lang, "CONVERTING"))

        dst = await conv.mp4_to_webm(src)
        if not dst:
            await message.answer(
                "❌ Konvertatsiya xatosi.\n"
                "FFmpeg serverda o‘rnatilmagan bo‘lishi mumkin."
            )
            return

        await message.answer_video(FSInputFile(dst), caption=t(lang, "DONE"))
        await db.inc_stat("mp4_to_webm")

        # Log kanal
        log_id = await db.get_setting("log_channel")
        if log_id:
            try:
                await bot.send_video(
                    chat_id=log_id,
                    video=FSInputFile(dst),
                    caption=f"🎥 MP4 → WEBM\n👤 {message.from_user.id}",
                )
            except Exception as e:
                print("log send error:", e)

        await state.clear()

    except Exception as e:
        print("mp4 handler error:", e)
        try:
            await message.answer(t(lang, "ERR_GENERIC"))
        except Exception:
            pass
    finally:
        conv.safe_remove(src, dst)


# ---------------- WEBM -> MP4 ----------------

@router.message(ConvState.wait_webm, F.video | F.document)
async def handle_webm(message: Message, state: FSMContext, bot: Bot):
    lang = await db.get_user_lang(message.from_user.id)

    file_id = None
    mime = ""
    fname = ""

    if message.video:
        file_id = message.video.file_id
        mime = (message.video.mime_type or "").lower()
        fname = (message.video.file_name or "").lower()
    elif message.document:
        file_id = message.document.file_id
        mime = (message.document.mime_type or "").lower()
        fname = (message.document.file_name or "").lower()

    if not file_id:
        await message.answer(t(lang, "ERR_NOT_WEBM"))
        return

    is_webm = "webm" in mime or fname.endswith(".webm")
    if not is_webm:
        await message.answer(t(lang, "ERR_NOT_WEBM"))
        return

    src = None
    dst = None
    try:
        src = await _download(bot, file_id, ".webm")
        if not src:
            await message.answer(t(lang, "ERR_GENERIC"))
            return

        await message.answer(t(lang, "CONVERTING_MP4"))

        dst = await conv.webm_to_mp4(src)
        if not dst:
            await message.answer(
                "❌ Konvertatsiya xatosi.\n"
                "FFmpeg serverda o‘rnatilmagan bo‘lishi mumkin."
            )
            return

        await message.answer_video(FSInputFile(dst), caption=t(lang, "DONE"))
        await db.inc_stat("webm_to_mp4")

        # Log kanal
        log_id = await db.get_setting("log_channel")
        if log_id:
            try:
                await bot.send_video(
                    chat_id=log_id,
                    video=FSInputFile(dst),
                    caption=f"🔄 WEBM → MP4\n👤 {message.from_user.id}",
                )
            except Exception as e:
                print("log send error:", e)

        await state.clear()

    except Exception as e:
        print("webm handler error:", e)
        try:
            await message.answer(t(lang, "ERR_GENERIC"))
        except Exception:
            pass
    finally:
        conv.safe_remove(src, dst)


# ---------------- Noto'g'ri fayl ----------------

@router.message(ConvState.wait_mp4)
async def wrong_mp4(message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    await message.answer(t(lang, "ERR_NOT_MP4"))


@router.message(ConvState.wait_webm)
async def wrong_webm(message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    await message.answer(t(lang, "ERR_NOT_WEBM"))
