import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.call import CallStatus
from app.models.user import User
from app.repositories.call_repository import CallRepository
from app.repositories.contact_repository import ContactRepository
from app.schemas.calls import CallInvitationOut, CallOut, IceServerOut, IceServersResponse

settings = get_settings()


class CallService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.call_repo = CallRepository(db)
        self.contact_repo = ContactRepository(db)

    async def create_call(self, current_user: User) -> CallOut:
        call = await self.call_repo.create_call(created_by_id=current_user.id)
        return CallOut.model_validate(call, from_attributes=True)

    async def get_call_by_code(self, code: str) -> CallOut:
        call = await self.call_repo.get_by_code(code.strip().upper())
        self._validate_joinable(call)
        return CallOut.model_validate(call, from_attributes=True)

    async def join_by_code(self, code: str) -> CallOut:
        """
        Valida que el código exista y no haya expirado. La conexión real a
        la sala ocurre por WebSocket (/ws/calls/{call_id}); este endpoint
        solo resuelve el código a la información de la llamada.
        """
        call = await self.call_repo.get_by_code(code.strip().upper())
        self._validate_joinable(call)
        return CallOut.model_validate(call, from_attributes=True)

    def _validate_joinable(self, call) -> None:
        if call is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Código de llamada inválido.")
        if call.status == CallStatus.ENDED:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="Esta llamada ya finalizó.")
        if call.status == CallStatus.WAITING:
            expires_at = call.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at < datetime.now(timezone.utc):
                raise HTTPException(status_code=status.HTTP_410_GONE, detail="El código de llamada expiró.")

    async def create_direct_call(self, current_user: User, contact_user_id: uuid.UUID) -> CallOut:
        if not await self.contact_repo.are_contacts(current_user.id, contact_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes llamar directamente a tus contactos.",
            )
        call = await self.call_repo.create_call(created_by_id=current_user.id)
        await self.call_repo.create_invitation(
            call_id=call.id, from_user_id=current_user.id, to_user_id=contact_user_id
        )
        return CallOut.model_validate(call, from_attributes=True)

    async def list_pending_invitations(self, current_user: User) -> list[CallInvitationOut]:
        invitations = await self.call_repo.list_pending_invitations(current_user.id)
        results = []
        for inv in invitations:
            call = await self.call_repo.get_by_id(inv.call_id)
            if call is None or call.status == CallStatus.ENDED:
                continue
            from_user = await self.db.get(User, inv.from_user_id)
            results.append(
                CallInvitationOut(
                    id=inv.id,
                    call_id=inv.call_id,
                    call_code=call.code,
                    from_user_id=inv.from_user_id,
                    from_username=from_user.username if from_user else "",
                    from_full_name=from_user.full_name if from_user else "",
                    status=inv.status,
                    created_at=inv.created_at,
                )
            )
        return results

    def get_ice_servers(self) -> IceServersResponse:
        servers = [IceServerOut(urls=settings.stun_server)]
        if settings.turn_server:
            servers.append(
                IceServerOut(
                    urls=settings.turn_server,
                    username=settings.turn_username or None,
                    credential=settings.turn_password or None,
                )
            )
        return IceServersResponse(ice_servers=servers)
