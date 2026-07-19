from gtts import gTTS
import time
from pathlib import Path

OUTPUT_DIR = Path("static")
OUTPUT_DIR.mkdir(exist_ok=True)

LANG_MAP = {"hi": "hi", "kn": "kn", "ta": "ta", "en": "en"}


def text_to_speech(text: str, lang: str = "hi") -> str | None:
    try:
        gtts_lang = LANG_MAP.get(lang, "hi")
        timestamp = int(time.time())
        filename = OUTPUT_DIR / f"reply_{timestamp}.mp3"

        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save(str(filename))

        return str(filename)
    except Exception as e:
        print(f"TTS error: {e}")
        return None