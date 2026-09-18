import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Contact(Base):
    """
    Relación de contacto confirmada.

    Se almacena una fila por dirección (A->B y B->A) para que las consultas
    "mis contactos" sean directas, sin necesidad de OR en ambos lados.
    Ambas filas se crean/eliminan siempre juntas desde el servicio.
    """
    __tablename__ = "contacts"
    __table_args__ = (UniqueConstraint("user_id", "contact_user_id", name="uq_contact_pair"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    contact_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
