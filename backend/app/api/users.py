from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import (
    MeResponse,
    PreferencesOut,
    PreferencesUpdate,
    ProfileOut,
    ProfileUpdate,
)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=MeResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return MeResponse(user=current_user, profile=current_user.profile, preferences=current_user.preferences)


@router.put("/me/profile", response_model=ProfileOut)
async def update_my_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = current_user.profile
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.put("/me/preferences", response_model=PreferencesOut)
async def update_my_preferences(
    payload: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    preferences = current_user.preferences
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(preferences, field, value)
    await db.commit()
    await db.refresh(preferences)
    return preferences
