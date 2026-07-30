import html
import re
import logging
import langid
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

_SHORT_CIRCUIT_THRESHOLD = 20
_MAX_CHARS = 4900


def _clean(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _is_english(text: str) -> bool:
    lang, conf = langid.classify(text)
    return lang == 'en' and conf > 0.5


def detect_language(text: str) -> str | None:
    text = _clean(text)
    if not text or len(text) < _SHORT_CIRCUIT_THRESHOLD:
        return 'en'
    try:
        lang, _ = langid.classify(text)
        return lang
    except Exception:
        return 'en'


def translate_to_english(text: str) -> str:
    text = _clean(text)
    if not text or len(text) < _SHORT_CIRCUIT_THRESHOLD:
        return text
    if _is_english(text):
        return text
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text[:_MAX_CHARS])
        return translated or text
    except Exception as e:
        logger.warning(f'Translation failed: {e}')
        return text


def translate_description(description: str) -> tuple[str, str, str]:
    if not description:
        return description, '', ''
    clean = _clean(description)
    if not clean or len(clean) < _SHORT_CIRCUIT_THRESHOLD:
        return clean, '', 'en'
    if _is_english(clean):
        return clean, '', 'en'
    try:
        lang = detect_language(clean)
        translated = GoogleTranslator(source='auto', target='en').translate(clean[:_MAX_CHARS])
        return (translated or clean), clean, lang or ''
    except Exception as e:
        logger.warning(f'Translation failed: {e}')
        return clean, '', 'en'
