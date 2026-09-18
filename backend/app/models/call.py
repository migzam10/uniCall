import enum
import secrets
import string
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

_CODE_ALPHABET = string.ascii_uppercase + string.digits
# Se excluyen caracteres ambiguos (0/O, 1/I) para que el código sea fácil
# de leer y compartir en voz alta o por chat.
_CODE_ALPHABET = _CODE_ALPHABET.translate(str.maketrans("", "", "01OI"))


def generate_call_code(length: int = 8) -> str:
    return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(length))


class CallStatus(str, enum.Enum):
    WAITING = "waiting"      # código generado, esperando que alguien se una
    ACTIVE = "active"        # al menos 2 participantes conectados
    ENDED = "ended"
    EXPIRED = "expired"      # nadie se unió antes de que expirara el código


class Call(Base):
    __tablename__ = "calls"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(12), unique=True, index=True, default=generate_call_code)
    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[CallStatus] = mapped_column(Enum(CallStatus), default=CallStatus.WAITING)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
