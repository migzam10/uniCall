import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call import Call, CallStatus, generate_call_code
from app.models.call_invitation import CallInvitation, CallInvitationStatus
from app.models.call_participant import CallParticipant

CALL_CODE_TTL_MINUTES = 30


class CallRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_call(self, created_by_id: uuid.UUID) -> Call:
        # Reintenta si por azar colisiona un código (extremadamente improbable
        # con el alfabeto usado, pero se maneja de forma explícita).
        for _ in range(5):
            code = generate_call_code()
            existing = await self.get_by_code(code)
            if existing is None:
                break
        else:
            raise RuntimeError("No se pudo generar un código de llamada único.")

        call = Call(
            code=code,
            created_by_id=created_by_id,
            status=CallStatus.WAITING,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=CALL_CODE_TTL_MINUTES),
        )
        self.db.add(call)
        await self.db.commit()
        await self.db.refresh(call)
        return call

    async def get_by_code(self, code: str) -> Call | None:
        stmt = select(Call).where(Call.code == code)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, call_id: uuid.UUID) -> Call | None:
        return await self.db.get(Call, call_id)

    async def mark_active(self, call: Call) -> None:
        if call.status == CallStatus.WAITING:
            call.status = CallStatus.ACTIVE
            call.started_at = datetime.now(timezone.utc)
            await self.db.commit()

    async def mark_ended(self, call: Call) -> None:
        call.status = CallStatus.ENDED
        call.ended_at = datetime.now(timezone.utc)
        await self.db.commit()

    async def add_participant(self, call_id: uuid.UUID, user_id: uuid.UUID) -> CallParticipant:
        participant = CallParticipant(call_id=call_id, user_id=user_id)
        self.db.add(participant)
        await self.db.commit()
        await self.db.refresh(participant)
        return participant

    async def mark_participant_left(self, call_id: uuid.UUID, user_id: uuid.UUID) -> None:
        stmt = select(CallParticipant).where(
            CallParticipant.call_id == call_id,
            CallParticipant.user_id == user_id,
            CallParticipant.left_at.is_(None),
        )
        result = await self.db.execute(stmt)
        participant = result.scalars().first()
        if participant is not None:
            participant.left_at = datetime.now(timezone.utc)
            await self.db.commit()

    async def count_active_participants(self, call_id: uuid.UUID) -> int:
        stmt = select(CallParticipant).where(
            CallParticipant.call_id == call_id, CallParticipant.left_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return len(result.scalars().all())

    # --- Invitaciones directas ---

    async def create_invitation(self, call_id: uuid.UUID, from_user_id: uuid.UUID, to_user_id: uuid.UUID) -> CallInvitation:
        invitation = CallInvitation(call_id=call_id, from_user_id=from_user_id, to_user_id=to_user_id)
        self.db.add(invitation)
        await self.db.commit()
        await self.db.refresh(invitation)
        return invitation

    async def list_pending_invitations(self, user_id: uuid.UUID) -> list[CallInvitation]:
        stmt = select(CallInvitation).where(
            CallInvitation.to_user_id == user_id, CallInvitation.status == CallInvitationStatus.PENDING
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
