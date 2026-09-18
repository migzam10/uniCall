import json
import tempfile
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.lsc.dtw import dtw_distance
from app.ai.lsc.landmark_extractor import VideoLandmarkExtractor
from app.core.config import get_settings
from app.core.storage import STORAGE_ROOT
from app.models.lsc_sign_template import LSCSignTemplate
from app.repositories.lsc_data_repository import LSCDataRepository
from app.schemas.lsc_data import ProcessVideoResponse, RecognizeResponse

settings = get_settings()


class LSCRecognitionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = LSCDataRepository(db)
        self._extractor = VideoLandmarkExtractor()

    async def process_video(self, video_id: uuid.UUID) -> ProcessVideoResponse:
        """
        Extrae landmarks de un video de referencia ya cargado y los guarda
        como plantilla (sección 12: dataset de entrenamiento separado del
        video crudo). Acción explícita del administrador, no automática.
        """
        video = await self.repo.get_video(video_id)
        if video is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video no encontrado.")

        video_path = STORAGE_ROOT / video.file_path
        if not video_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El archivo de video no existe en disco.")

        sequence, hand_frames = self._extractor.extract_from_file(str(video_path))

        if not sequence:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No se pudo leer el video (formato no soportado o archivo corrupto).",
            )
        if hand_frames == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No se detectaron manos en el video. Verifica que la persona esté visible y bien iluminada.",
            )

        existing = await self.repo.get_template_for_video(video_id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Este video ya fue procesado anteriormente."
            )

        template = LSCSignTemplate(
            sign_id=video.sign_id,
            video_id=video.id,
            landmark_sequence=json.dumps(sequence),
            frame_count=len(sequence),
            hand_detection_frames=hand_frames,
        )
        template = await self.repo.save_template(template)

        return ProcessVideoResponse(
            template_id=template.id,
            frame_count=template.frame_count,
            hand_detection_frames=template.hand_detection_frames,
        )

    async def recognize(self, upload: UploadFile) -> RecognizeResponse:
        """
        Reconoce la seña realizada en un clip corto, comparándolo (DTW)
        contra las plantillas de señas publicadas.

        Nunca "inventa" una respuesta (sección 29): si la mejor coincidencia
        supera el umbral de distancia configurado, se informa que no hubo
        reconocimiento en vez de devolver una seña incorrecta con falsa
        confianza.
        """
        templates = await self.repo.list_templates_for_published_signs()
        if not templates:
            return RecognizeResponse(
                matched=False,
                message="Todavía no hay señas publicadas con plantillas procesadas para comparar.",
            )

        with tempfile.TemporaryDirectory() as tmp_dir:
            clip_path = Path(tmp_dir) / "clip.mp4"
            clip_path.write_bytes(await upload.read())
            sequence, hand_frames = self._extractor.extract_from_file(str(clip_path))

        if not sequence:
            return RecognizeResponse(matched=False, message="No se pudo leer el video enviado.")
        if hand_frames == 0:
            return RecognizeResponse(
                matched=False, message="No se detectaron manos en el video. Intenta de nuevo con mejor iluminación."
            )

        best_distance = float("inf")
        best_template: LSCSignTemplate | None = None
        best_sign = None

        for template, sign in templates:
            reference_sequence = json.loads(template.landmark_sequence)
            distance = dtw_distance(sequence, reference_sequence)
            if distance < best_distance:
                best_distance = distance
                best_template = template
                best_sign = sign

        if best_template is None or best_sign is None:
            return RecognizeResponse(matched=False, message="No se encontró una coincidencia.")

        # Confianza aproximada: decae con la distancia, acotada a [0, 1].
        confidence = max(0.0, 1.0 - (best_distance / settings.lsc_max_dtw_distance))

        if best_distance > settings.lsc_max_dtw_distance:
            return RecognizeResponse(
                matched=False,
                message="No se reconoció ninguna seña con suficiente confianza.",
                closest_word=best_sign.word,
                confidence=round(confidence, 3),
            )

        return RecognizeResponse(
            matched=True,
            sign_id=best_sign.id,
            word=best_sign.word,
            meaning=best_sign.meaning,
            confidence=round(confidence, 3),
        )
