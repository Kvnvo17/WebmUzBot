from locales import uz, ru, en

LOCALES = {"uz": uz, "ru": ru, "en": en}


def t(lang: str, key: str) -> str:
    lang = lang if lang in LOCALES else "uz"
    return getattr(LOCALES[lang], key, getattr(uz, key, key))
