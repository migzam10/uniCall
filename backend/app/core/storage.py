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
LSC_ANIMATIONS_DIR = STORAGE_ROOT / "lsc_animations"

ALLOWED_VIDEO_CONTENT_TYPES = {"video/mp4", "video/webm", "video/quicktime", "video/x-matroska"}
MAX_VIDEO_SIZE_BYTES = 200 * 1024 * 1024  # 200 MB

# .glb/.gltf no tienen un content-type MIME estándar (los navegadores y
# clientes mandan cosas como application/octet-stream u application/json
# indistintamente), así que las animaciones se validan por extensión de
# archivo en vez de por content_type, a diferencia de los videos.
ALLOWED_ANIMATION_EXTENSIONS = {".glb", ".gltf"}
MAX_ANIMATION_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB


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


async def save_lsc_animation(upload: UploadFile) -> tuple[str, int]:
    """
    Guarda una animación 3D (.glb/.gltf) subida en disco.

    Devuelve (ruta_relativa, tamaño_en_bytes). Lanza InvalidUploadError si
    la extensión no es una animación soportada o excede el tamaño máximo.
    """
    extension = Path(upload.filename or "").suffix.lower()
    if extension not in ALLOWED_ANIMATION_EXTENSIONS:
        raise InvalidUploadError(
            f"Extensión de archivo no soportada: {extension or '(sin extensión)'}. "
            f"Formatos permitidos: {', '.join(sorted(ALLOWED_ANIMATION_EXTENSIONS))}."
        )

    LSC_ANIMATIONS_DIR.mkdir(parents=True, exist_ok=True)

    unique_name = f"{uuid.uuid4()}{extension}"
    destination = LSC_ANIMATIONS_DIR / unique_name

    size = 0
    chunk_size = 1024 * 1024  # 1 MB
    with destination.open("wb") as out_file:
        while chunk := await upload.read(chunk_size):
            size += len(chunk)
            if size > MAX_ANIMATION_SIZE_BYTES:
                out_file.close()
                destination.unlink(missing_ok=True)
                raise InvalidUploadError(
                    f"La animación excede el tamaño máximo permitido "
                    f"({MAX_ANIMATION_SIZE_BYTES // (1024 * 1024)} MB)."
                )
            out_file.write(chunk)

    relative_path = f"lsc_animations/{unique_name}"
    return relative_path, size


def resolve_animation_url(relative_path: str) -> str:
    return f"{settings.app_base_url}/media/{relative_path}"


def delete_lsc_animation(relative_path: str) -> None:
    path = STORAGE_ROOT / relative_path
    path.unlink(missing_ok=True)
