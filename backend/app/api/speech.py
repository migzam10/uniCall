from fastapi import APIRouter, Depends, UploadFile

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.speech import SynthesizeRequest, SynthesizeResponse, TranscribeResponse
from app.services.speech_service import speech_service

router = APIRouter(prefix="/api/v1/speech", tags=["speech"])


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    audio: UploadFile,
    language: str = "es",
    current_user: User = Depends(get_current_user),
):
    """
    Español hablado -> texto (sección 8, primer tramo del flujo).

    Recibe un archivo de audio (WAV recomendado) y devuelve el texto
    transcrito. En fases posteriores, este texto alimenta el motor de
    interpretación lingüística español -> LSC.
    """
    audio_bytes = await audio.read()
    return await speech_service.transcribe(audio_bytes, language=language)


@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_speech(
    payload: SynthesizeRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Texto -> voz (sección 9, último tramo del flujo LSC -> español).

    En fases posteriores, el texto de entrada vendrá del motor de
    interpretación LSC -> español; por ahora este endpoint es
    independiente y reutilizable.
    """
    return await speech_service.synthesize(payload.text, voice=payload.voice.value, language=payload.language)
