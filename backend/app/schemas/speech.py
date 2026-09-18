from pydantic import BaseModel, Field

from app.models.user_preferences import VoicePreference


class TranscribeResponse(BaseModel):
    text: str
    language: str


class SynthesizeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    voice: VoicePreference = VoicePreference.FEMENINA
    language: str = "es"


class SynthesizeResponse(BaseModel):
    audio_base64: str
    mime_type: str = "audio/wav"
