import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CallInvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class CallInvitation(Base):
    """
    Invitación directa a un contacto (sección 5: "iniciar videollamada
    directamente"), independiente de compartir el código manualmente.

    El receptor puede consultar sus invitaciones pendientes vía polling
    (GET /calls/invitations) o, cuando se implemente en una fase posterior,
    recibirlas por un canal de notificaciones en tiempo real.
    """
    __tablename__ = "call_invitations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    call_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"))
    from_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    to_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[CallInvitationStatus] = mapped_column(
        Enum(CallInvitationStatus), default=CallInvitationStatus.PENDING
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
