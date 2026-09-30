from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.lsc_data import (
    RecognizeResponse,
    TranslateTextRequest,
    TranslationSequenceEnriched,
)
from app.services.lsc_recognition_service import LSCRecognitionService
from app.services.lsc_data_service import LSCDataService

router = APIRouter(prefix="/api/v1/lsc", tags=["lsc-recognition"])


@router.post("/recognize", response_model=RecognizeResponse)
async def recognize_sign(
    video: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    LSC -> texto (sección 9, primer tramo): recibe un clip corto de la
    persona sorda realizando una seña y devuelve la palabra reconocida,
    si hay una coincidencia con suficiente confianza.
    """
    return await LSCRecognitionService(db).recognize(video)


@router.post("/translate", response_model=TranslationSequenceEnriched)
async def translate_text_to_lsc(
    request: TranslateTextRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Traducción (Fase 6): recibe un texto en español, aplica NLP y devuelve
    la secuencia de IDs de animaciones LSC enriquecida con las URLs de los 
    avatares 3D (.glb).
    """
    from app.ai.translation.nlp_engine import translate_text_to_sign_sequence
    # 1. Obtener los IDs crudos desde el motor NLP
    raw_sequence = await translate_text_to_sign_sequence(db, request.text)
    
    # 2. Enriquecer con los links a las animaciones 3D
    service = LSCDataService(db)
    return await service.enrich_translation_sequence(request.text, raw_sequence)
