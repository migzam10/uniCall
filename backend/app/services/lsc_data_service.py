import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import (
    InvalidUploadError,
    delete_lsc_animation,
    delete_lsc_video,
    resolve_animation_url,
    resolve_video_url,
    save_lsc_animation,
    save_lsc_video,
)
from app.models.lsc_animation import LSCAnimation
from app.models.lsc_category import LSCCategory, slugify
from app.models.lsc_phrase import LSCPhrase, LSCPhraseSign
from app.models.lsc_sign import LSCSign
from app.models.lsc_video import LSCVideo
from app.models.user import User
from app.repositories.lsc_data_repository import LSCDataRepository
from app.schemas.lsc_data import (
    AnimationOut,
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    PhraseCreate,
    PhraseOut,
    PhraseSignOut,
    PhraseUpdate,
    SignCreate,
    SignOut,
    SignUpdate,
    SignWithVideosOut,
    TranslationItemEnriched,
    TranslationSequenceEnriched,
    VideoOut,
)


class LSCDataService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = LSCDataRepository(db)

    # --- Categorías ---

    async def create_category(self, payload: CategoryCreate) -> CategoryOut:
        slug = slugify(payload.name)
        if await self.repo.get_category_by_slug(slug) is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una categoría similar.")

        category = LSCCategory(name=payload.name.strip(), slug=slug, description=payload.description)
        category = await self.repo.create_category(category)
        return CategoryOut.model_validate(category)

    async def update_category(self, category_id: uuid.UUID, payload: CategoryUpdate) -> CategoryOut:
        category = await self.repo.get_category(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada.")

        data = payload.model_dump(exclude_unset=True)
        if "name" in data:
            category.name = data["name"].strip()
            category.slug = slugify(category.name)
        if "description" in data:
            category.description = data["description"]
        if "is_active" in data:
            category.is_active = data["is_active"]

        await self.repo.save()
        return CategoryOut.model_validate(category)

    async def list_categories(self, include_inactive: bool) -> list[CategoryOut]:
        categories = await self.repo.list_categories(include_inactive)
        return [CategoryOut.model_validate(c) for c in categories]

    # --- Señas ---

    async def create_sign(self, payload: SignCreate, current_user: User) -> SignOut:
        category = await self.repo.get_category(payload.category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada.")

        sign = LSCSign(
            category_id=payload.category_id,
            word=payload.word.strip(),
            meaning=payload.meaning.strip(),
            description=payload.description,
            tags=payload.tags,
            created_by_id=current_user.id,
        )
        sign = await self.repo.create_sign(sign)
        return SignOut.model_validate(sign)

    async def update_sign(self, sign_id: uuid.UUID, payload: SignUpdate) -> SignOut:
        sign = await self.repo.get_sign(sign_id)
        if sign is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seña no encontrada.")

        if payload.category_id is not None:
            category = await self.repo.get_category(payload.category_id)
            if category is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada.")
            sign.category_id = payload.category_id

        data = payload.model_dump(exclude_unset=True, exclude={"bump_version", "category_id"})
        for field in ("word", "meaning", "description", "tags", "status", "is_active"):
            if field in data:
                value = data[field]
                setattr(sign, field, value.strip() if isinstance(value, str) and field in ("word", "meaning") else value)

        if payload.bump_version:
            sign.version += 1

        await self.repo.save()
        await self.db.refresh(sign)
        return SignOut.model_validate(sign)

    async def list_signs(self, category_id: uuid.UUID | None, include_inactive: bool) -> list[SignOut]:
        signs = await self.repo.list_signs(category_id, include_inactive)
        return [SignOut.model_validate(s) for s in signs]

    async def get_sign_with_videos(self, sign_id: uuid.UUID) -> SignWithVideosOut:
        sign = await self.repo.get_sign_with_videos(sign_id)
        if sign is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seña no encontrada.")
        return SignWithVideosOut(
            **SignOut.model_validate(sign).model_dump(),
            videos=[self._video_to_out(v) for v in sign.videos],
            animations=[self._animation_to_out(a) for a in sign.animations],
        )

    # --- Videos ---

    def _video_to_out(self, video: LSCVideo) -> VideoOut:
        return VideoOut(
            id=video.id,
            sign_id=video.sign_id,
            url=resolve_video_url(video.file_path),
            original_filename=video.original_filename,
            content_type=video.content_type,
            size_bytes=video.size_bytes,
            is_active=video.is_active,
            created_at=video.created_at,
        )

    async def upload_video(self, sign_id: uuid.UUID, upload: UploadFile, current_user: User) -> VideoOut:
        sign = await self.repo.get_sign(sign_id)
        if sign is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seña no encontrada.")

        try:
            relative_path, size = await save_lsc_video(upload)
        except InvalidUploadError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        video = LSCVideo(
            sign_id=sign_id,
            file_path=relative_path,
            original_filename=upload.filename or "video",
            content_type=upload.content_type or "video/mp4",
            size_bytes=size,
            uploaded_by_id=current_user.id,
        )
        video = await self.repo.add_video(video)
        return self._video_to_out(video)

    async def list_videos(self, sign_id: uuid.UUID) -> list[VideoOut]:
        videos = await self.repo.list_videos_for_sign(sign_id)
        return [self._video_to_out(v) for v in videos]

    async def delete_video(self, video_id: uuid.UUID) -> None:
        video = await self.repo.get_video(video_id)
        if video is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video no encontrado.")
        delete_lsc_video(video.file_path)
        await self.repo.delete_video(video)

    # --- Animaciones del avatar 3D (Fase 6) ---

    def _animation_to_out(self, animation: LSCAnimation) -> AnimationOut:
        return AnimationOut(
            id=animation.id,
            sign_id=animation.sign_id,
            url=resolve_animation_url(animation.file_path),
            original_filename=animation.original_filename,
            content_type=animation.content_type,
            size_bytes=animation.size_bytes,
            is_active=animation.is_active,
            created_at=animation.created_at,
        )

    async def upload_animation(self, sign_id: uuid.UUID, upload: UploadFile, current_user: User) -> AnimationOut:
        sign = await self.repo.get_sign(sign_id)
        if sign is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seña no encontrada.")

        try:
            relative_path, size = await save_lsc_animation(upload)
        except InvalidUploadError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        animation = LSCAnimation(
            sign_id=sign_id,
            file_path=relative_path,
            original_filename=upload.filename or "animation.glb",
            content_type=upload.content_type or "application/octet-stream",
            size_bytes=size,
            uploaded_by_id=current_user.id,
        )
        animation = await self.repo.add_animation(animation)
        return self._animation_to_out(animation)

    async def list_animations(self, sign_id: uuid.UUID) -> list[AnimationOut]:
        animations = await self.repo.list_animations_for_sign(sign_id)
        return [self._animation_to_out(a) for a in animations]

    async def delete_animation(self, animation_id: uuid.UUID) -> None:
        animation = await self.repo.get_animation(animation_id)
        if animation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animación no encontrada.")
        delete_lsc_animation(animation.file_path)
        await self.repo.delete_animation(animation)

    async def enrich_translation_sequence(
        self, original_text: str, raw_sequence: list[dict]
    ) -> TranslationSequenceEnriched:
        """
        Recibe la secuencia cruda del motor NLP (app/ai/translation/nlp_engine.py,
        Fase 6 IA — cada item con `word`/`sign_id`/`found_in_db`) y la enriquece
        con disponibilidad de animación 3D consultando LSCAnimation.

        Política explícita (sección 29, "nunca inventar" — cierra el punto
        pendiente de README §5.1): si una palabra no tiene seña documentada
        (`found_in_db=False`) o tiene seña pero sin animación cargada
        (`has_animation=False`), NUNCA se inventa un avatar para esa palabra;
        el llamador (frontend) debe mostrar solo el subtítulo de esa palabra.
        `complete=False` si falta cualquiera de las dos cosas en cualquier
        palabra, para que el frontend avise que la traducción es incompleta.
        """
        items: list[TranslationItemEnriched] = []
        for raw in raw_sequence:
            sign_id = raw.get("sign_id")
            animation_url: str | None = None
            has_animation = False

            if sign_id is not None:
                animation = await self.repo.get_latest_active_animation_for_sign(uuid.UUID(str(sign_id)))
                if animation is not None:
                    has_animation = True
                    animation_url = resolve_animation_url(animation.file_path)

            items.append(
                TranslationItemEnriched(
                    word=raw["word"],
                    sign_id=sign_id,
                    found_in_db=raw["found_in_db"],
                    has_animation=has_animation,
                    animation_url=animation_url,
                )
            )

        complete = all(item.found_in_db and item.has_animation for item in items)
        return TranslationSequenceEnriched(original_text=original_text, sequence=items, complete=complete)

    # --- Frases ---

    async def create_phrase(self, payload: PhraseCreate, current_user: User) -> PhraseOut:
        sign_ids = [item.sign_id for item in payload.signs]
        for sign_id in sign_ids:
            if await self.repo.get_sign(sign_id) is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"La seña {sign_id} no existe."
                )

        positions = [item.position for item in payload.signs]
        if len(positions) != len(set(positions)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Las posiciones de la secuencia deben ser únicas."
            )

        phrase = LSCPhrase(text=payload.text.strip(), description=payload.description, created_by_id=current_user.id)
        phrase_signs = [LSCPhraseSign(sign_id=item.sign_id, position=item.position) for item in payload.signs]
        phrase = await self.repo.create_phrase(phrase, phrase_signs)
        return await self._phrase_to_out(phrase)

    async def update_phrase(self, phrase_id: uuid.UUID, payload: PhraseUpdate) -> PhraseOut:
        phrase = await self.repo.get_phrase(phrase_id)
        if phrase is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Frase no encontrada.")

        data = payload.model_dump(exclude_unset=True, exclude={"signs"})
        for field in ("text", "description", "is_active"):
            if field in data:
                value = data[field]
                setattr(phrase, field, value.strip() if field == "text" and isinstance(value, str) else value)

        if payload.signs is not None:
            for item in payload.signs:
                if await self.repo.get_sign(item.sign_id) is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail=f"La seña {item.sign_id} no existe."
                    )
            positions = [item.position for item in payload.signs]
            if len(positions) != len(set(positions)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Las posiciones de la secuencia deben ser únicas.",
                )
            new_signs = [LSCPhraseSign(sign_id=item.sign_id, position=item.position) for item in payload.signs]
            await self.repo.replace_phrase_signs(phrase_id, new_signs)

        await self.repo.save()
        return await self._phrase_to_out(phrase)

    async def list_phrases(self, include_inactive: bool) -> list[PhraseOut]:
        phrases = await self.repo.list_phrases(include_inactive)
        return [await self._phrase_to_out(p) for p in phrases]

    async def _phrase_to_out(self, phrase: LSCPhrase) -> PhraseOut:
        rows = await self.repo.get_phrase_signs(phrase.id)
        return PhraseOut(
            id=phrase.id,
            text=phrase.text,
            description=phrase.description,
            is_active=phrase.is_active,
            created_at=phrase.created_at,
            signs=[PhraseSignOut(sign_id=sign.id, word=sign.word, position=ps.position) for ps, sign in rows],
        )
