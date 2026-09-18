import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LSCSignTemplate(Base):
    """
    Secuencia de landmarks precomputada a partir de un video de referencia,
    usada como plantilla para comparar (vía DTW) contra clips nuevos.

    Se genera explícitamente (acción del administrador: "procesar video"),
    nunca automáticamente al subir el archivo — mantiene separados, como
    pide la sección 12, el dato crudo (video) del dato derivado usado por
    el modelo (plantilla de landmarks).
    """
    __tablename__ = "lsc_sign_templates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    sign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lsc_signs.id", ondelete="CASCADE"))
    video_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lsc_videos.id", ondelete="CASCADE"))

    # Secuencia de vectores de landmarks, serializada como JSON.
    landmark_sequence: Mapped[str] = mapped_column(Text, nullable=False)
    frame_count: Mapped[int] = mapped_column(Integer, nullable=False)
    hand_detection_frames: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
