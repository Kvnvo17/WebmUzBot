import os
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
        await message.answer(t(await db.get_user_lang(message.from_user.id), "SUB_REQUIRED"))
        return
    lang = await db.get_user_lang(message.from_user.id)
    await state.set_state(ConvState.wait_mp4)
    await message.answer(t(lang, "ASK_MP4"))


@router.message(F.text.in_(BTN_WEBM))
async def ask_webm(message: Message, state: FSMContext, bot: Bot):
    if not await is_subscribed(bot, message.from_user.id):
        await message.answer(t(await db.get_user_lang(message.from_user.id), "SUB_REQUIRED"))
        return
    lang = await db.get_user_lang(message.from_user.id)
    await state.set_state(ConvState.wait_webm)
    await message.answer(t(lang, "ASK_WEBM"))


async def _download(bot: Bot, file_id: str, suffix: str) -> str | None:
    try:
        f = await bot.get_file(file_id)
        import tempfile, uuid
        path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}{suffix}")
        await bot.download_file(f.file_path, path)
        return path
    except Exception as e:
        print("download error:", e)
        return None


@router.message(ConvState.wait_mp4, F.video)
async def handle_mp4(message: Message, state: FSMContext, bot: Bot):
    lang = await db.get_user_lang(message.from_user.id)
    video = message.video
    src = None
    dst = None

    mime = (video.mime_type or "").lower()
    fname = (video.file_name or "").lower()
    if "mp4" not in mime and not fname.endswith(".mp4"):
        await message.answer(t(lang, "ERR_NOT_MP4"))
        return

    try:
        src = await _download(bot, video.file_id, ".mp4")
        if not src:
            await message.answer(t(lang, "ERR_GENERIC"))
            return

        info = await conv.get_video_info(src)
        if not info:
            await message.answer(t(lang, "ERR_GENERIC"))
            return
        w, h, dur = info
        if w != 512 or h != 512:
            await message.answer(t(lang, "ERR_SIZE"))
            return
        if dur > 3.05:
            await message.answer(t(lang, "ERR_DURATION"))
            return

        await message.answer(t(lang, "CONVERTING"))

        dst = await conv.mp4_to_webm(src)
        if not dst:
            await message.answer(t(lang, "ERR_GENERIC"))
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


@router.message(ConvState.wait_webm, F.video | F.document)
async def handle_webm(message: Message, state: FSMContext, bot: Bot):
    lang = await db.get_user_lang(message.from_user.id)
    file_id = None
    fname = ""
    mime = ""

    if message.video:
        file_id = message.video.file_id
        mime = (message.video.mime_type or "").lower()
        fname = (message.video.file_name or "").lower()
    elif message.document:
        file_id = message.document.file_id
        mime = (message.document.mime_type or "").lower()
        fname = (message.document.file_name or "").lower()

    if not file_id or ("webm" not in mime and not fname.endswith(".webm")):
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
            await message.answer(t(lang, "ERR_GENERIC"))
            return

        await message.answer_video(FSInputFile(dst), caption=t(lang, "DONE"))
        await db.inc_stat("webm_to_mp4")
        await state.clear()
    except Exception as e:
        print("webm handler error:", e)
        try:
            await message.answer(t(lang, "ERR_GENERIC"))
        except Exception:
            pass
    finally:
        conv.safe_remove(src, dst)


@router.message(ConvState.wait_mp4)
async def wrong_mp4(message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    await message.answer(t(lang, "ERR_NOT_MP4"))


@router.message(ConvState.wait_webm)
async def wrong_webm(message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    await message.answer(t(lang, "ERR_NOT_WEBM"))
