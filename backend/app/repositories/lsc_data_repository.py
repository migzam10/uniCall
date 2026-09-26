import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.lsc_animation import LSCAnimation
from app.models.lsc_category import LSCCategory
from app.models.lsc_phrase import LSCPhrase, LSCPhraseSign
from app.models.lsc_sign import LSCSign, LSCSignStatus
from app.models.lsc_sign_template import LSCSignTemplate
from app.models.lsc_video import LSCVideo


class LSCDataRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Categorías ---

    async def create_category(self, category: LSCCategory) -> LSCCategory:
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def get_category_by_slug(self, slug: str) -> LSCCategory | None:
        result = await self.db.execute(select(LSCCategory).where(LSCCategory.slug == slug))
        return result.scalar_one_or_none()

    async def get_category(self, category_id: uuid.UUID) -> LSCCategory | None:
        return await self.db.get(LSCCategory, category_id)

    async def list_categories(self, include_inactive: bool = True) -> list[LSCCategory]:
        stmt = select(LSCCategory).order_by(LSCCategory.name)
        if not include_inactive:
            stmt = stmt.where(LSCCategory.is_active.is_(True))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def save(self) -> None:
        await self.db.commit()

    # --- Señas ---

    async def create_sign(self, sign: LSCSign) -> LSCSign:
        self.db.add(sign)
        await self.db.commit()
        await self.db.refresh(sign)
        return sign

    async def get_sign(self, sign_id: uuid.UUID) -> LSCSign | None:
        return await self.db.get(LSCSign, sign_id)

    async def get_sign_with_videos(self, sign_id: uuid.UUID) -> LSCSign | None:
        stmt = (
            select(LSCSign)
            .where(LSCSign.id == sign_id)
            .options(selectinload(LSCSign.videos), selectinload(LSCSign.animations))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_signs(
        self, category_id: uuid.UUID | None = None, include_inactive: bool = True
    ) -> list[LSCSign]:
        stmt = select(LSCSign).order_by(LSCSign.word)
        if category_id is not None:
            stmt = stmt.where(LSCSign.category_id == category_id)
        if not include_inactive:
            stmt = stmt.where(LSCSign.is_active.is_(True))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # --- Videos ---

    async def add_video(self, video: LSCVideo) -> LSCVideo:
        self.db.add(video)
        await self.db.commit()
        await self.db.refresh(video)
        return video

    async def get_video(self, video_id: uuid.UUID) -> LSCVideo | None:
        return await self.db.get(LSCVideo, video_id)

    async def list_videos_for_sign(self, sign_id: uuid.UUID) -> list[LSCVideo]:
        stmt = select(LSCVideo).where(LSCVideo.sign_id == sign_id).order_by(LSCVideo.created_at)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_video(self, video: LSCVideo) -> None:
        await self.db.delete(video)
        await self.db.commit()

    # --- Animaciones (Fase 6) ---

    async def add_animation(self, animation: LSCAnimation) -> LSCAnimation:
        self.db.add(animation)
        await self.db.commit()
        await self.db.refresh(animation)
        return animation

    async def get_animation(self, animation_id: uuid.UUID) -> LSCAnimation | None:
        return await self.db.get(LSCAnimation, animation_id)

    async def list_animations_for_sign(self, sign_id: uuid.UUID) -> list[LSCAnimation]:
        stmt = select(LSCAnimation).where(LSCAnimation.sign_id == sign_id).order_by(LSCAnimation.created_at)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_animation(self, animation: LSCAnimation) -> None:
        await self.db.delete(animation)
        await self.db.commit()

    async def get_latest_active_animation_for_sign(self, sign_id: uuid.UUID) -> LSCAnimation | None:
        """Animación más reciente activa de una seña, usada al enriquecer /translate."""
        stmt = (
            select(LSCAnimation)
            .where(LSCAnimation.sign_id == sign_id, LSCAnimation.is_active.is_(True))
            .order_by(LSCAnimation.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # --- Frases ---

    async def create_phrase(self, phrase: LSCPhrase, phrase_signs: list[LSCPhraseSign]) -> LSCPhrase:
        self.db.add(phrase)
        await self.db.flush()
        for ps in phrase_signs:
            ps.phrase_id = phrase.id
            self.db.add(ps)
        await self.db.commit()
        await self.db.refresh(phrase)
        return phrase

    async def get_phrase(self, phrase_id: uuid.UUID) -> LSCPhrase | None:
        return await self.db.get(LSCPhrase, phrase_id)

    async def get_phrase_signs(self, phrase_id: uuid.UUID) -> list[tuple[LSCPhraseSign, LSCSign]]:
        stmt = (
            select(LSCPhraseSign, LSCSign)
            .join(LSCSign, LSCSign.id == LSCPhraseSign.sign_id)
            .where(LSCPhraseSign.phrase_id == phrase_id)
            .order_by(LSCPhraseSign.position)
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def replace_phrase_signs(self, phrase_id: uuid.UUID, phrase_signs: list[LSCPhraseSign]) -> None:
        existing = await self.db.execute(select(LSCPhraseSign).where(LSCPhraseSign.phrase_id == phrase_id))
        for row in existing.scalars().all():
            await self.db.delete(row)
        await self.db.flush()
        for ps in phrase_signs:
            ps.phrase_id = phrase_id
            self.db.add(ps)
        await self.db.commit()

    async def list_phrases(self, include_inactive: bool = True) -> list[LSCPhrase]:
        stmt = select(LSCPhrase).order_by(LSCPhrase.text)
        if not include_inactive:
            stmt = stmt.where(LSCPhrase.is_active.is_(True))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # --- Plantillas de landmarks (Fase 5) ---

    async def save_template(self, template: LSCSignTemplate) -> LSCSignTemplate:
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def get_template_for_video(self, video_id: uuid.UUID) -> LSCSignTemplate | None:
        stmt = select(LSCSignTemplate).where(LSCSignTemplate.video_id == video_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_templates_for_published_signs(self) -> list[tuple[LSCSignTemplate, LSCSign]]:
        """Plantillas cuya seña está publicada y activa (candidatas válidas para reconocimiento)."""
        stmt = (
            select(LSCSignTemplate, LSCSign)
            .join(LSCSign, LSCSign.id == LSCSignTemplate.sign_id)
            .where(LSCSign.status == LSCSignStatus.PUBLISHED, LSCSign.is_active.is_(True))
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]
