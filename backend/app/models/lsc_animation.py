import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LSCAnimation(Base):
    """
    Animación 3D del avatar para una seña (Fase 6): un archivo `.glb`/`.gltf`
    autocontenido (malla + animación ya "horneada"), vinculado a una LSCSign.

    Mismo patrón de almacenamiento que LSCVideo (ver app/core/storage.py):
    el archivo vive en disco local, la arquitectura permite migrar a
    almacenamiento externo sin cambiar este modelo.
    """
    __tablename__ = "lsc_animations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    sign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lsc_signs.id", ondelete="CASCADE"))

    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sign: Mapped["LSCSign"] = relationship(back_populates="animations")
