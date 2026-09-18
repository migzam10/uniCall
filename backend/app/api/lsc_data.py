import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.user import User, UserRole
from app.schemas.lsc_data import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    PhraseCreate,
    PhraseOut,
    PhraseUpdate,
    ProcessVideoResponse,
    SignCreate,
    SignOut,
    SignUpdate,
    SignWithVideosOut,
    VideoOut,
)
from app.services.lsc_data_service import LSCDataService
from app.services.lsc_recognition_service import LSCRecognitionService

router = APIRouter(
    prefix="/api/v1/admin/lsc",
    tags=["lsc-data"],
    dependencies=[Depends(require_roles(UserRole.ADMINISTRADOR))],
)


# --- Categorías ---

@router.post("/categories", response_model=CategoryOut, status_code=201)
async def create_category(payload: CategoryCreate, db: AsyncSession = Depends(get_db)):
    return await LSCDataService(db).create_category(payload)


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(include_inactive: bool = True, db: AsyncSession = Depends(get_db)):
    return await LSCDataService(db).list_categories(include_inactive)


@router.patch("/categories/{category_id}", response_model=CategoryOut)
async def update_category(category_id: uuid.UUID, payload: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    return await LSCDataService(db).update_category(category_id, payload)


# --- Señas ---

@router.post("/signs", response_model=SignOut, status_code=201)
async def create_sign(
    payload: SignCreate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRADOR)),
    db: AsyncSession = Depends(get_db),
):
    return await LSCDataService(db).create_sign(payload, current_user)


@router.get("/signs", response_model=list[SignOut])
async def list_signs(
    category_id: uuid.UUID | None = None,
    include_inactive: bool = True,
    db: AsyncSession = Depends(get_db),
):
    return await LSCDataService(db).list_signs(category_id, include_inactive)


@router.get("/signs/{sign_id}", response_model=SignWithVideosOut)
async def get_sign(sign_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await LSCDataService(db).get_sign_with_videos(sign_id)


@router.patch("/signs/{sign_id}", response_model=SignOut)
async def update_sign(sign_id: uuid.UUID, payload: SignUpdate, db: AsyncSession = Depends(get_db)):
    return await LSCDataService(db).update_sign(sign_id, payload)


# --- Videos ---

@router.post("/signs/{sign_id}/videos", response_model=VideoOut, status_code=201)
async def upload_sign_video(
    sign_id: uuid.UUID,
    video: UploadFile = File(...),
    current_user: User = Depends(require_roles(UserRole.ADMINISTRADOR)),
    db: AsyncSession = Depends(get_db),
):
    """Carga un video de referencia para una seña (sección 12)."""
    return await LSCDataService(db).upload_video(sign_id, video, current_user)


@router.get("/signs/{sign_id}/videos", response_model=list[VideoOut])
async def list_sign_videos(sign_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await LSCDataService(db).list_videos(sign_id)


@router.delete("/videos/{video_id}", status_code=204)
async def delete_video(video_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await LSCDataService(db).delete_video(video_id)
    return None


@router.post("/videos/{video_id}/process", response_model=ProcessVideoResponse, status_code=201)
async def process_video(video_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Extrae landmarks del video y los guarda como plantilla para el
    reconocimiento (Fase 5). Acción explícita, separada de la carga del
    video (sección 12).
    """
    return await LSCRecognitionService(db).process_video(video_id)


# --- Frases ---

@router.post("/phrases", response_model=PhraseOut, status_code=201)
async def create_phrase(
    payload: PhraseCreate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRADOR)),
    db: AsyncSession = Depends(get_db),
):
    return await LSCDataService(db).create_phrase(payload, current_user)


@router.get("/phrases", response_model=list[PhraseOut])
async def list_phrases(include_inactive: bool = True, db: AsyncSession = Depends(get_db)):
    return await LSCDataService(db).list_phrases(include_inactive)


@router.patch("/phrases/{phrase_id}", response_model=PhraseOut)
async def update_phrase(phrase_id: uuid.UUID, payload: PhraseUpdate, db: AsyncSession = Depends(get_db)):
    return await LSCDataService(db).update_phrase(phrase_id, payload)
