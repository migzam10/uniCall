import re
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = (
        value.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        .replace("ñ", "n")
    )
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return value or "categoria"


class LSCCategory(Base):
    """
    Categoría del árbol de contenido LSC (sección 11), por ejemplo:
    saludos, personas, lugares, acciones, objetos, alimentos, emociones.
    """
    __tablename__ = "lsc_categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
