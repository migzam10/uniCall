"""
Interfaz abstracta del motor de reconocimiento de LSC (sección 13: "AI
Engine"). El resto de la aplicación depende únicamente de esta interfaz.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LSCRecognitionResult:
    matched: bool
    sign_id: str | None = None
    word: str | None = None
    meaning: str | None = None
    confidence: float | None = None  # 0.0 a 1.0
    message: str | None = None  # explicación cuando matched=False


class LSCRecognizer(ABC):
    @abstractmethod
    async def recognize(self, video_bytes: bytes) -> LSCRecognitionResult:
        """Recibe un clip de video y devuelve la seña reconocida, si la hay."""
        raise NotImplementedError
