import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.contacts import ContactOut, ContactRequestCreate, ContactRequestOut, UserSearchResult
from app.services.contact_service import ContactService

router = APIRouter(prefix="/api/v1/contacts", tags=["contacts"])


@router.get("/search", response_model=list[UserSearchResult])
async def search_users(
    q: str = Query(min_length=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ContactService(db).search_users(q, current_user)


@router.get("", response_model=list[ContactOut])
async def list_my_contacts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ContactService(db).list_contacts(current_user)


@router.delete("/{contact_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(
    contact_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ContactService(db).remove_contact(current_user, contact_user_id)
    return None


@router.post("/requests", response_model=ContactRequestOut, status_code=status.HTTP_201_CREATED)
async def send_contact_request(
    payload: ContactRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ContactService(db).send_request(current_user, payload.to_username)


@router.get("/requests/incoming", response_model=list[ContactRequestOut])
async def list_incoming_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ContactService(db).list_incoming(current_user)


@router.get("/requests/outgoing", response_model=list[ContactRequestOut])
async def list_outgoing_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ContactService(db).list_outgoing(current_user)


@router.post("/requests/{request_id}/accept", status_code=status.HTTP_204_NO_CONTENT)
async def accept_contact_request(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ContactService(db).respond_to_request(current_user, request_id, accept=True)
    return None


@router.post("/requests/{request_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_contact_request(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ContactService(db).respond_to_request(current_user, request_id, accept=False)
    return None
