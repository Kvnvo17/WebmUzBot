from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Adminlar", callback_data="adm:admins")],
        [InlineKeyboardButton(text="📢 Reklama", callback_data="adm:ads")],
        [InlineKeyboardButton(text="📋 Majburiy obuna", callback_data="adm:subs")],
        [InlineKeyboardButton(text="📥 Log kanal", callback_data="adm:log")],
        [InlineKeyboardButton(text="📝 Start xabari", callback_data="adm:start")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="adm:stats")],
        [InlineKeyboardButton(text="🔙 Bosh menyu", callback_data="adm:close")],
    ])


def admins_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Admin qo‘shish", callback_data="adm:admin_add")],
        [InlineKeyboardButton(text="🗑 Admin o‘chirish", callback_data="adm:admin_del")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:back")],
    ])


def subs_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Kanal qo‘shish", callback_data="adm:sub_add")],
        [InlineKeyboardButton(text="🗑 Kanal o‘chirish", callback_data="adm:sub_del")],
        [InlineKeyboardButton(text="📋 Ro‘yxat", callback_data="adm:sub_list")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:back")],
    ])


def log_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Log kanal qo‘shish", callback_data="adm:log_add")],
        [InlineKeyboardButton(text="🗑 Log kanalni o‘chirish", callback_data="adm:log_del")],
        [InlineKeyboardButton(text="📋 Hozirgi log kanal", callback_data="adm:log_show")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:back")],
    ])


def start_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 UZ start", callback_data="adm:start_uz")],
        [InlineKeyboardButton(text="🇷🇺 RU start", callback_data="adm:start_ru")],
        [InlineKeyboardButton(text="🇬🇧 EN start", callback_data="adm:start_en")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:back")],
    ])


def ads_lang_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O‘zbek", callback_data="adm:ads_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="adm:ads_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="adm:ads_en")],
        [InlineKeyboardButton(text="🌍 Barchaga", callback_data="adm:ads_all")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:back")],
    ])
