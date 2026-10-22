import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import Profile
from app.models.user import User
from app.models.user_preferences import UserPreferences


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.profile), selectinload(User.preferences))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, identifier: str) -> User | None:
        clean_id = identifier.strip().lower()
        stmt = (
            select(User)
            .where(
                or_(
                    func.lower(User.username) == clean_id,
                    func.lower(User.email) == clean_id,
                )
            )
            .options(selectinload(User.profile), selectinload(User.preferences))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_username_or_email(self, username: str, email: str) -> bool:
        clean_username = username.strip().lower()
        clean_email = email.strip().lower()
        stmt = select(User.id).where(
            or_(
                func.lower(User.username) == clean_username,
                func.lower(User.email) == clean_email,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(self, *, username: str, email: str, hashed_password: str, full_name: str, role) -> User:
        user = User(
            username=username.strip(),
            email=email.strip().lower(),
            hashed_password=hashed_password,
            full_name=full_name.strip(),
            role=role,
        )
        self.db.add(user)
        await self.db.flush()

        # Cada usuario nuevo obtiene un Profile y Preferences por defecto (sección 4 y 20)
        self.db.add(Profile(user_id=user.id))
        self.db.add(UserPreferences(user_id=user.id))

        await self.db.commit()
        await self.db.refresh(user)
        return await self.get_by_id(user.id)

    async def update_password(self, user: User, hashed_password: str) -> None:
        user.hashed_password = hashed_password
        await self.db.commit()
