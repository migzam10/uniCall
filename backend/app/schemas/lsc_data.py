import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.lsc_sign import LSCSignStatus


# --- Categorías ---

class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    is_active: bool
    created_at: datetime


# --- Señas ---

class SignCreate(BaseModel):
    category_id: uuid.UUID
    word: str = Field(min_length=1, max_length=150)
    meaning: str = Field(min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=1000)
    tags: str | None = Field(default=None, max_length=300)


class SignUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    word: str | None = Field(default=None, min_length=1, max_length=150)
    meaning: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=1000)
    tags: str | None = Field(default=None, max_length=300)
    status: LSCSignStatus | None = None
    is_active: bool | None = None
    # Si es True, incrementa `version` (sección 12: versionar cuando sea
    # necesario). Se deja explícito para que la persona administradora
    # decida cuándo un cambio amerita una nueva versión (p. ej. corrección
    # lingüística) vs. un ajuste menor (p. ej. arreglar una errata).
    bump_version: bool = False


class SignOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    word: str
    meaning: str
    description: str | None
    tags: str | None
    status: LSCSignStatus
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SignWithVideosOut(SignOut):
    videos: list["VideoOut"] = []
    animations: list["AnimationOut"] = []


# --- Videos ---

class VideoOut(BaseModel):
    id: uuid.UUID
    sign_id: uuid.UUID
    url: str
    original_filename: str
    content_type: str
    size_bytes: int
    is_active: bool
    created_at: datetime


# --- Animaciones del avatar 3D (Fase 6) ---

class AnimationOut(BaseModel):
    id: uuid.UUID
    sign_id: uuid.UUID
    url: str
    original_filename: str
    content_type: str
    size_bytes: int
    is_active: bool
    created_at: datetime


class TranslationItemEnriched(BaseModel):
    """
    Item de una secuencia de traducción (texto -> LSC) ya enriquecido con
    disponibilidad de animación 3D. `word`/`sign_id`/`found_in_db` vienen
    del motor NLP (app/ai/translation/nlp_engine.py, Fase 6 IA); esta clase
    vive en la capa de datos LSC para no acoplar el motor NLP a la tabla de
    animaciones — se conecta desde el servicio (ver
    LSCDataService.enrich_translation_sequence).
    """
    word: str
    sign_id: uuid.UUID | None = None
    found_in_db: bool
    # Sección 29 ("nunca inventar"): si la seña no está documentada o no
    # tiene animación cargada todavía, has_animation queda en False y el
    # frontend debe mostrar solo el subtítulo de esa palabra, nunca un
    # avatar inventado.
    has_animation: bool
    animation_url: str | None = None


class TranslationSequenceEnriched(BaseModel):
    original_text: str
    sequence: list[TranslationItemEnriched]
    # False si alguna palabra no tiene seña documentada o animación cargada
    # (sección 29): el frontend debe avisar que la traducción es incompleta.
    complete: bool


# --- Frases ---

class PhraseSignItem(BaseModel):
    sign_id: uuid.UUID
    position: int = Field(ge=0)


class PhraseCreate(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=1000)
    signs: list[PhraseSignItem] = Field(min_length=1)


class PhraseUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool | None = None
    signs: list[PhraseSignItem] | None = None


class PhraseSignOut(BaseModel):
    sign_id: uuid.UUID
    word: str
    position: int


class PhraseOut(BaseModel):
    id: uuid.UUID
    text: str
    description: str | None
    is_active: bool
    created_at: datetime
    signs: list[PhraseSignOut]


# --- Reconocimiento de LSC (Fase 5) ---

class ProcessVideoResponse(BaseModel):
    template_id: uuid.UUID
    frame_count: int
    hand_detection_frames: int


class RecognizeResponse(BaseModel):
    matched: bool
    sign_id: uuid.UUID | None = None
    word: str | None = None
    meaning: str | None = None
    confidence: float | None = None
    message: str | None = None
    closest_word: str | None = None
