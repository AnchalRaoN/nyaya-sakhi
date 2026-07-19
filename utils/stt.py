import httpx
import os
import tempfile
import whisper
import traceback

_model = None

def _get_model():
    global _model
    if _model is None:
        print("Loading Whisper model (first time only)...")
        _model = whisper.load_model("small")
        print("Whisper model loaded successfully.")
    return _model


async def transcribe_audio(media_url: str) -> str | None:
    try:
        auth = (
            os.getenv("TWILIO_ACCOUNT_SID", ""),
            os.getenv("TWILIO_AUTH_TOKEN", "")
        )
        print(f"Downloading audio from: {media_url}")
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(media_url, auth=auth)
            resp.raise_for_status()
            audio_bytes = resp.content
        print(f"Downloaded {len(audio_bytes)} bytes")

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        model = _get_model()
        print("Starting transcription...")
        result = model.transcribe(tmp_path)
        text = result.get("text", "").strip()
        print(f"Transcription result: '{text}'")

        os.remove(tmp_path)
        return text if text else None

    except Exception as e:
        print(f"STT error: {e}")
        print(traceback.format_exc())
        return None