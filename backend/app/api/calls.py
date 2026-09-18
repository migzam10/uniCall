import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.calls import (
    CallInvitationOut,
    CallOut,
    DirectCallRequest,
    IceServersResponse,
    JoinCallRequest,
)
from app.services.call_service import CallService

router = APIRouter(prefix="/api/v1/calls", tags=["calls"])


@router.post("", response_model=CallOut, status_code=201)
async def create_call(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Crea una llamada y genera un código/enlace de invitación (sección 6)."""
    return await CallService(db).create_call(current_user)


@router.post("/join", response_model=CallOut)
async def join_call_by_code(
    payload: JoinCallRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CallService(db).join_by_code(payload.code)


@router.get("/code/{code}", response_model=CallOut)
async def get_call_by_code(
    code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CallService(db).get_call_by_code(code)


@router.post("/direct", response_model=CallOut, status_code=201)
async def create_direct_call(
    payload: DirectCallRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Llama directamente a un contacto ya agregado (sección 5)."""
    return await CallService(db).create_direct_call(current_user, payload.contact_user_id)


@router.get("/invitations", response_model=list[CallInvitationOut])
async def list_pending_invitations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CallService(db).list_pending_invitations(current_user)


@router.get("/ice-servers", response_model=IceServersResponse)
async def get_ice_servers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return CallService(db).get_ice_servers()
