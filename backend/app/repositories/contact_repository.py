import uuid

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.models.contact_request import ContactRequest, ContactRequestStatus
from app.models.user import User


class ContactRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_users(self, query: str, exclude_user_id: uuid.UUID, limit: int = 20) -> list[User]:
        stmt = (
            select(User)
            .where(
                User.id != exclude_user_id,
                User.is_active.is_(True),
                or_(User.username.ilike(f"%{query}%"), User.full_name.ilike(f"%{query}%")),
            )
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_pending_request(self, from_user_id: uuid.UUID, to_user_id: uuid.UUID) -> ContactRequest | None:
        stmt = select(ContactRequest).where(
            or_(
                and_(ContactRequest.from_user_id == from_user_id, ContactRequest.to_user_id == to_user_id),
                and_(ContactRequest.from_user_id == to_user_id, ContactRequest.to_user_id == from_user_id),
            ),
            ContactRequest.status == ContactRequestStatus.PENDING,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def are_contacts(self, user_id: uuid.UUID, other_user_id: uuid.UUID) -> bool:
        stmt = select(Contact.id).where(Contact.user_id == user_id, Contact.contact_user_id == other_user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create_request(self, from_user_id: uuid.UUID, to_user_id: uuid.UUID) -> ContactRequest:
        req = ContactRequest(from_user_id=from_user_id, to_user_id=to_user_id)
        self.db.add(req)
        await self.db.commit()
        await self.db.refresh(req)
        return req

    async def get_request_by_id(self, request_id: uuid.UUID) -> ContactRequest | None:
        return await self.db.get(ContactRequest, request_id)

    async def list_incoming_requests(self, user_id: uuid.UUID) -> list[tuple[ContactRequest, User]]:
        stmt = (
            select(ContactRequest, User)
            .join(User, User.id == ContactRequest.from_user_id)
            .where(ContactRequest.to_user_id == user_id, ContactRequest.status == ContactRequestStatus.PENDING)
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def list_outgoing_requests(self, user_id: uuid.UUID) -> list[tuple[ContactRequest, User]]:
        stmt = (
            select(ContactRequest, User)
            .join(User, User.id == ContactRequest.to_user_id)
            .where(ContactRequest.from_user_id == user_id, ContactRequest.status == ContactRequestStatus.PENDING)
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def accept_request(self, request: ContactRequest) -> None:
        request.status = ContactRequestStatus.ACCEPTED
        # Se crean ambas direcciones de la relación de contacto.
        self.db.add(Contact(user_id=request.from_user_id, contact_user_id=request.to_user_id))
        self.db.add(Contact(user_id=request.to_user_id, contact_user_id=request.from_user_id))
        await self.db.commit()

    async def reject_request(self, request: ContactRequest) -> None:
        request.status = ContactRequestStatus.REJECTED
        await self.db.commit()

    async def list_contacts(self, user_id: uuid.UUID) -> list[tuple[Contact, User]]:
        stmt = (
            select(Contact, User)
            .join(User, User.id == Contact.contact_user_id)
            .where(Contact.user_id == user_id)
            .order_by(User.full_name)
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def remove_contact(self, user_id: uuid.UUID, contact_user_id: uuid.UUID) -> None:
        stmt = select(Contact).where(
            or_(
                and_(Contact.user_id == user_id, Contact.contact_user_id == contact_user_id),
                and_(Contact.user_id == contact_user_id, Contact.contact_user_id == user_id),
            )
        )
        result = await self.db.execute(stmt)
        for contact in result.scalars().all():
            await self.db.delete(contact)
        await self.db.commit()

    async def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
