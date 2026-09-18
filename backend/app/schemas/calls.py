import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.call import CallStatus
from app.models.call_invitation import CallInvitationStatus


class CallOut(BaseModel):
    id: uuid.UUID
    code: str
    status: CallStatus
    created_by_id: uuid.UUID
    created_at: datetime
    expires_at: datetime
    started_at: datetime | None
    ended_at: datetime | None


class JoinCallRequest(BaseModel):
    code: str


class DirectCallRequest(BaseModel):
    contact_user_id: uuid.UUID


class CallInvitationOut(BaseModel):
    id: uuid.UUID
    call_id: uuid.UUID
    call_code: str
    from_user_id: uuid.UUID
    from_username: str
    from_full_name: str
    status: CallInvitationStatus
    created_at: datetime


class IceServerOut(BaseModel):
    urls: str
    username: str | None = None
    credential: str | None = None


class IceServersResponse(BaseModel):
    ice_servers: list[IceServerOut]
