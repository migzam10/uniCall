"""
Interfaces abstractas del motor de voz.

Siguiendo la sección 13 de la especificación ("AI Engine"), el resto de la
aplicación (servicios, API) depende únicamente de estas interfaces, nunca
de una implementación concreta. Así, cambiar de motor de reconocimiento o
síntesis de voz no requiere modificar los endpoints ni la lógica de negocio.
"""
from abc import ABC, abstractmethod


class SpeechRecognizer(ABC):
    """Motor de reconocimiento de voz (Español hablado -> texto)."""

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, language: str = "es") -> str:
        """Recibe audio (WAV) y devuelve el texto transcrito."""
        raise NotImplementedError


class SpeechSynthesizer(ABC):
    """Motor de síntesis de voz (texto -> audio)."""

    @abstractmethod
    async def synthesize(self, text: str, voice: str, language: str = "es") -> bytes:
        """
        Recibe texto y devuelve audio en formato WAV.

        `voice` es "masculina" o "femenina" (ver VoicePreference en
        app.models.user_preferences).
        """
        raise NotImplementedError
