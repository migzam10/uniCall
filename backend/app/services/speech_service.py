import base64

from fastapi import HTTPException, status

from app.ai.base import SpeechRecognizer, SpeechSynthesizer
from app.ai.speech.mock_recognizer import MockRecognizer
from app.ai.tts.espeak_synthesizer import EspeakSynthesizer
from app.core.config import get_settings
from app.schemas.speech import SynthesizeResponse, TranscribeResponse

settings = get_settings()


def _build_recognizer() -> SpeechRecognizer:
    if settings.stt_engine == "whisper":
        from app.ai.speech.whisper_recognizer import WhisperRecognizer

        return WhisperRecognizer()
    return MockRecognizer()


def _build_synthesizer() -> SpeechSynthesizer:
    return EspeakSynthesizer()


class SpeechService:
    def __init__(self) -> None:
        self._recognizer = _build_recognizer()
        self._synthesizer = _build_synthesizer()

    async def transcribe(self, audio_bytes: bytes, language: str = "es") -> TranscribeResponse:
        if not audio_bytes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se recibió audio.")
        try:
            text = await self._recognizer.transcribe(audio_bytes, language=language)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return TranscribeResponse(text=text, language=language)

    async def synthesize(self, text: str, voice: str, language: str = "es") -> SynthesizeResponse:
        try:
            audio_bytes = await self._synthesizer.synthesize(text, voice=voice, language=language)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
        return SynthesizeResponse(audio_base64=base64.b64encode(audio_bytes).decode("ascii"), mime_type="audio/wav")


# Instancia única: evita recargar el motor de STT (potencialmente pesado)
# en cada request.
speech_service = SpeechService()
