import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LSCSignStatus(str, enum.Enum):
    DRAFT = "draft"          # cargada pero pendiente de revisión lingüística
    PUBLISHED = "published"  # validada y disponible para el dataset
    ARCHIVED = "archived"    # retirada (no se elimina, para trazabilidad)


class LSCSign(Base):
    """
    Una seña documentada de LSC: palabra/significado + metadatos.

    Sección 29: nunca se inventan señas. Cada registro representa material
    documentado (manual de LSC / videos de referencia), con separación
    explícita entre "dato cargado" (draft) y "dato validado" (published),
    en línea con la sección 12: no promover contenido a producción sin un
    proceso de revisión.
    """
    __tablename__ = "lsc_signs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lsc_categories.id", ondelete="RESTRICT"))

    word: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    meaning: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    # Etiquetas simples separadas por coma (p. ej. "formal,saludo,mañana").
    # Se mantiene como texto plano para no sobre-diseñar antes de tener
    # casos de uso reales de búsqueda avanzada por etiqueta.
    tags: Mapped[str | None] = mapped_column(String(300), nullable=True)

    status: Mapped[LSCSignStatus] = mapped_column(Enum(LSCSignStatus), default=LSCSignStatus.DRAFT)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    videos: Mapped[list["LSCVideo"]] = relationship(back_populates="sign", cascade="all, delete-orphan")
