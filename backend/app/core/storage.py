"""
Almacenamiento de archivos subidos (videos de referencia de LSC).

Implementación: sistema de archivos local del servidor, servido vía
StaticFiles de FastAPI bajo /media (ver app/main.py). La arquitectura
mantiene esto detrás de una función simple (`save_upload`) para poder
migrar a almacenamiento externo (S3, GCS, etc.) en el futuro sin tocar los
modelos de datos ni los endpoints — solo esta función y `resolve_url`.
"""
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings

settings = get_settings()

STORAGE_ROOT = Path(__file__).resolve().parent.parent.parent / "storage"
LSC_VIDEOS_DIR = STORAGE_ROOT / "lsc_videos"

ALLOWED_VIDEO_CONTENT_TYPES = {"video/mp4", "video/webm", "video/quicktime", "video/x-matroska"}
MAX_VIDEO_SIZE_BYTES = 200 * 1024 * 1024  # 200 MB


class InvalidUploadError(Exception):
    pass


async def save_lsc_video(upload: UploadFile) -> tuple[str, int]:
    """
    Guarda un video subido en disco.

    Devuelve (ruta_relativa, tamaño_en_bytes). Lanza InvalidUploadError si
    el tipo de contenido no es un video soportado o excede el tamaño máximo.
    """
    if upload.content_type not in ALLOWED_VIDEO_CONTENT_TYPES:
        raise InvalidUploadError(
            f"Tipo de archivo no soportado: {upload.content_type}. "
            f"Formatos permitidos: {', '.join(sorted(ALLOWED_VIDEO_CONTENT_TYPES))}."
        )

    LSC_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

    extension = Path(upload.filename or "").suffix or ".mp4"
    unique_name = f"{uuid.uuid4()}{extension}"
    destination = LSC_VIDEOS_DIR / unique_name

    size = 0
    chunk_size = 1024 * 1024  # 1 MB
    with destination.open("wb") as out_file:
        while chunk := await upload.read(chunk_size):
            size += len(chunk)
            if size > MAX_VIDEO_SIZE_BYTES:
                out_file.close()
                destination.unlink(missing_ok=True)
                raise InvalidUploadError(
                    f"El video excede el tamaño máximo permitido ({MAX_VIDEO_SIZE_BYTES // (1024 * 1024)} MB)."
                )
            out_file.write(chunk)

    relative_path = f"lsc_videos/{unique_name}"
    return relative_path, size


def resolve_video_url(relative_path: str) -> str:
    return f"{settings.app_base_url}/media/{relative_path}"


def delete_lsc_video(relative_path: str) -> None:
    path = STORAGE_ROOT / relative_path
    path.unlink(missing_ok=True)
