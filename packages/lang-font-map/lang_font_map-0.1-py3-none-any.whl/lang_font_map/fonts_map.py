"""
Language to Font mapping dictionary.
This module provides font family names for different languages using Google Fonts.
"""

# Language to Google Font family mapping
LANG_FONT_MAP = {
    # Indian Languages
    "hin_Deva": "Noto Sans Devanagari",  # Hindi
    "guj_Gujr": "Noto Sans Gujarati",  # Gujarati
    "ben_Beng": "Noto Sans Bengali",  # Bengali
    "mar_Deva": "Noto Sans Devanagari",  # Marathi
    "tel_Telu": "Noto Sans Telugu",  # Telugu
    "kan_Knda": "Noto Sans Kannada",  # Kannada
    "mal_Mlym": "Noto Sans Malayalam",  # Malayalam
    "tam_Taml": "Noto Sans Tamil",  # Tamil
    "pan_Guru": "Noto Sans Gurmukhi",  # Punjabi
    "ori_Orya": "Noto Sans Oriya",  # Odia
    "asm_Beng": "Noto Sans Bengali",  # Assamese
    "awa_Deva": "Noto Sans Devanagari",  # Awadhi
    "bho_Deva": "Noto Sans Devanagari",  # Bhojpuri
    "hne_Deva": "Noto Sans Devanagari",  # Chhattisgarhi
    "mag_Deva": "Noto Sans Devanagari",  # Magahi
    "mai_Deva": "Noto Sans Devanagari",  # Maithili
    "mni_Beng": "Noto Sans Bengali",  # Meitei
    "npi_Deva": "Noto Sans Devanagari",  # Nepali
    "san_Deva": "Noto Sans Devanagari",  # Sanskrit
    
    # East Asian Languages
    "zho_Hans": "Noto Sans SC",  # Simplified Chinese
    "zho_Hant": "Noto Sans TC",  # Traditional Chinese
    "jpn_Jpan": "Noto Sans JP",  # Japanese
    "kor_Hang": "Noto Sans KR",  # Korean
    "bod_Tibt": "Noto Sans Tibetan",  # Tibetan
    "mya_Mymr": "Noto Sans Myanmar",  # Burmese
    "khm_Khmr": "Noto Sans Khmer",  # Khmer
    "lao_Laoo": "Noto Sans Lao",  # Lao
    "shn_Mymr": "Noto Sans Myanmar",  # Shan
    "yue_Hant": "Noto Sans TC",  # Yue Chinese
    
    # Middle Eastern Languages
    "arb_Arab": "Noto Sans Arabic",  # Arabic
    "fas_Arab": "Noto Sans Arabic",  # Persian
    "urd_Arab": "Noto Sans Arabic",  # Urdu
    
    # European Languages
    "rus_Cyrl": "Noto Sans",  # Russian
    "ukr_Cyrl": "Noto Sans",  # Ukrainian
    "bul_Cyrl": "Noto Sans",  # Bulgarian
    
    # Latin Script Languages
    "eng_Latn": "Noto Sans",  # English
    "fra_Latn": "Noto Sans",  # French
    "deu_Latn": "Noto Sans",  # German
    "spa_Latn": "Noto Sans",  # Spanish
    "ita_Latn": "Noto Sans",  # Italian
    "por_Latn": "Noto Sans",  # Portuguese
    
    # Default fallback font
    "default": "Noto Sans"
}

def get_font_family(lang_code):
    """
    Get the Google Font family name for a language code.
    
    Args:
        lang_code (str): Language code (e.g., 'hin_Deva' for Hindi)
    
    Returns:
        str: Google Font family name
    """
    return LANG_FONT_MAP.get(lang_code, LANG_FONT_MAP["default"])

def get_google_fonts_url(lang_code):
    """
    Get the Google Fonts URL for a language.
    
    Args:
        lang_code (str): Language code (e.g., 'hin_Deva' for Hindi)
    
    Returns:
        str: Google Fonts URL
    """
    font_family = get_font_family(lang_code)
    # Replace spaces with + for URL
    font_family_url = font_family.replace(" ", "+")
    return f"https://fonts.googleapis.com/css2?family={font_family_url}&display=swap"