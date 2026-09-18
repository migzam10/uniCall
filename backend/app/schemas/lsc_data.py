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
