import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LSCPhrase(Base):
    """
    Frase en español documentada junto con la secuencia de señas que la
    componen (sección 10: el reconocimiento trabaja con secuencias, no solo
    señas individuales; sección 29: se diferencia explícitamente palabra,
    seña, frase y estructura lingüística).
    """
    __tablename__ = "lsc_phrases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class LSCPhraseSign(Base):
    """
    Asociación ordenada entre una frase y las señas que la componen, en
    secuencia (posición 0, 1, 2, ...).
    """
    __tablename__ = "lsc_phrase_signs"
    __table_args__ = (UniqueConstraint("phrase_id", "position", name="uq_phrase_position"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phrase_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lsc_phrases.id", ondelete="CASCADE"))
    sign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lsc_signs.id", ondelete="RESTRICT"))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
