from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from locales import t


def main_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "BTN_MP4_TO_WEBM")),
             KeyboardButton(text=t(lang, "BTN_WEBM_TO_MP4"))],
            [KeyboardButton(text=t(lang, "BTN_LANG")),
             KeyboardButton(text=t(lang, "BTN_GUIDE"))],
        ],
        resize_keyboard=True,
    )


def lang_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O‘zbek", callback_data="lang:uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en")],
    ])


def subscribe_menu(channels, lang: str) -> InlineKeyboardMarkup:
    rows = []
    for ch in channels:
        url = ch["chat_id"] if str(ch["chat_id"]).startswith("http") else f"https://t.me/{str(ch['chat_id']).lstrip('@')}"
        rows.append([InlineKeyboardButton(text=f"📢 {ch['title']}", url=url)])
    rows.append([InlineKeyboardButton(text=t(lang, "SUB_CHECK"), callback_data="sub:check")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
