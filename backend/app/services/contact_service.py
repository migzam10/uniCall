import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact_request import ContactRequestStatus
from app.models.user import User
from app.repositories.contact_repository import ContactRepository
from app.schemas.contacts import ContactOut, ContactRequestOut, UserSearchResult


class ContactService:
    def __init__(self, db: AsyncSession):
        self.repo = ContactRepository(db)

    async def search_users(self, query: str, current_user: User) -> list[UserSearchResult]:
        if len(query.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ingresa al menos 2 caracteres para buscar.",
            )
        users = await self.repo.search_users(query.strip(), exclude_user_id=current_user.id)
        return [UserSearchResult.model_validate(u) for u in users]

    async def send_request(self, current_user: User, to_username: str) -> ContactRequestOut:
        if to_username == current_user.username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes agregarte a ti mismo.")

        target = await self.repo.get_user_by_username(to_username)
        if target is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

        if await self.repo.are_contacts(current_user.id, target.id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya son contactos.")

        existing = await self.repo.get_pending_request(current_user.id, target.id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una solicitud pendiente entre ambos usuarios.",
            )

        req = await self.repo.create_request(current_user.id, target.id)
        return ContactRequestOut(
            id=req.id,
            from_user_id=req.from_user_id,
            to_user_id=req.to_user_id,
            status=req.status,
            created_at=req.created_at,
            other_username=target.username,
            other_full_name=target.full_name,
        )

    async def respond_to_request(
        self, current_user: User, request_id: uuid.UUID, accept: bool
    ) -> None:
        req = await self.repo.get_request_by_id(request_id)
        if req is None or req.to_user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada.")
        if req.status != ContactRequestStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Esta solicitud ya fue respondida.")

        if accept:
            await self.repo.accept_request(req)
        else:
            await self.repo.reject_request(req)

    async def list_incoming(self, current_user: User) -> list[ContactRequestOut]:
        rows = await self.repo.list_incoming_requests(current_user.id)
        return [
            ContactRequestOut(
                id=req.id,
                from_user_id=req.from_user_id,
                to_user_id=req.to_user_id,
                status=req.status,
                created_at=req.created_at,
                other_username=user.username,
                other_full_name=user.full_name,
            )
            for req, user in rows
        ]

    async def list_outgoing(self, current_user: User) -> list[ContactRequestOut]:
        rows = await self.repo.list_outgoing_requests(current_user.id)
        return [
            ContactRequestOut(
                id=req.id,
                from_user_id=req.from_user_id,
                to_user_id=req.to_user_id,
                status=req.status,
                created_at=req.created_at,
                other_username=user.username,
                other_full_name=user.full_name,
            )
            for req, user in rows
        ]

    async def list_contacts(self, current_user: User) -> list[ContactOut]:
        rows = await self.repo.list_contacts(current_user.id)
        return [
            ContactOut(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                role=user.role,
                contact_since=contact.created_at,
            )
            for contact, user in rows
        ]

    async def remove_contact(self, current_user: User, contact_user_id: uuid.UUID) -> None:
        await self.repo.remove_contact(current_user.id, contact_user_id)
