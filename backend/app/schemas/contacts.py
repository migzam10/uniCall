import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.contact_request import ContactRequestStatus
from app.models.user import UserRole


class UserSearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    full_name: str
    role: UserRole


class ContactOut(BaseModel):
    id: uuid.UUID
    username: str
    full_name: str
    role: UserRole
    contact_since: datetime


class ContactRequestCreate(BaseModel):
    to_username: str


class ContactRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    from_user_id: uuid.UUID
    to_user_id: uuid.UUID
    status: ContactRequestStatus
    created_at: datetime

    # Datos del otro usuario, para que la UI no tenga que hacer otra consulta
    other_username: str
    other_full_name: str
