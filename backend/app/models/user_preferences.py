"""
Preferencias del usuario relacionadas con accesibilidad y traducción.

Esta tabla se ampliará en fases posteriores (más voces, más idiomas, etc.)
sin romper la estructura actual, según la sección 21 de la especificación.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VoicePreference(str, enum.Enum):
    MASCULINA = "masculina"
    FEMENINA = "femenina"


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    # Preferencias de comunicación (definidas en el registro, sección 4)
    preferred_language: Mapped[str] = mapped_column(String(20), default="es-CO")
    sign_language: Mapped[str] = mapped_column(String(20), default="LSC")

    # Preferencias de traducción durante la llamada
    auto_translate_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    show_subtitles: Mapped[bool] = mapped_column(Boolean, default=True)
    show_avatar: Mapped[bool] = mapped_column(Boolean, default=True)
    voice_output_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    voice_preference: Mapped[VoicePreference] = mapped_column(
        Enum(VoicePreference), default=VoicePreference.FEMENINA
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="preferences")
