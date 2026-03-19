"""
Internationalization (i18n) Support
Vietnamese + English translations
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional

# Get i18n directory
I18N_DIR = Path(__file__).parent

# Load translations
_translations: Dict[str, Dict[str, str]] = {}

def load_translations():
    """Load all translation files"""
    global _translations
    
    for lang_file in I18N_DIR.glob("*.json"):
        lang_code = lang_file.stem  # vi, en
        try:
            with open(lang_file, "r", encoding="utf-8") as f:
                _translations[lang_code] = json.load(f)
            print(f"✓ Loaded {lang_code} translations")
        except Exception as e:
            print(f"✗ Error loading {lang_code}: {e}")

# Load on import
load_translations()

def get_language(request_headers: dict, default: str = "vi") -> str:
    """
    Detect language from request headers
    Supports: vi (Vietnamese), en (English)
    """
    accept_language = request_headers.get("accept-language", "")
    
    # Parse Accept-Language header
    # Examples: "en-US,en;q=0.9,vi;q=0.8"
    if "en" in accept_language.lower():
        return "en"
    elif "vi" in accept_language.lower():
        return "vi"
    
    return default

def t(key: str, lang: str = "vi", **kwargs) -> str:
    """
    Translate a key
    
    Args:
        key: Translation key (e.g., "api.error.not_found")
        lang: Language code ("vi" or "en")
        **kwargs: Variables to format into translation
    
    Returns:
        Translated string
    
    Example:
        t("api.error.not_found", lang="en")
        t("api.quota_exceeded", lang="vi", limit=100)
    """
    # Get translation dict for language
    lang_dict = _translations.get(lang, _translations.get("vi", {}))
    
    # Navigate nested keys (e.g., "api.error.not_found")
    keys = key.split(".")
    value = lang_dict
    
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            break
    
    # If translation not found, return key
    if not isinstance(value, str):
        return key
    
    # Format with variables
    try:
        return value.format(**kwargs)
    except KeyError:
        return value

def get_translations(lang: str = "vi") -> dict:
    """Get all translations for a language"""
    return _translations.get(lang, _translations.get("vi", {}))
