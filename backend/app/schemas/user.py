import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole
from app.models.user_preferences import VoicePreference


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    avatar_url: str | None = None
    bio: str | None = None
    phone_number: str | None = None
    location: str | None = None


class ProfileUpdate(BaseModel):
    avatar_url: str | None = None
    bio: str | None = None
    phone_number: str | None = None
    location: str | None = None


class PreferencesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    preferred_language: str
    sign_language: str
    auto_translate_enabled: bool
    show_subtitles: bool
    show_avatar: bool
    voice_output_enabled: bool
    voice_preference: VoicePreference


class PreferencesUpdate(BaseModel):
    auto_translate_enabled: bool | None = None
    show_subtitles: bool | None = None
    show_avatar: bool | None = None
    voice_output_enabled: bool | None = None
    voice_preference: VoicePreference | None = None


class MeResponse(BaseModel):
    user: UserOut
    profile: ProfileOut
    preferences: PreferencesOut
