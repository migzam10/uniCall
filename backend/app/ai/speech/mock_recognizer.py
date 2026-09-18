"""
Motor de reconocimiento de voz simulado.

Se usa en pruebas automatizadas y en desarrollo local cuando no se quiere
(o no se puede) descargar el modelo de Whisper. Nunca debe usarse en
producción — el servicio valida esto vía configuración (ver
app/services/speech_service.py).
"""
from app.ai.base import SpeechRecognizer


class MockRecognizer(SpeechRecognizer):
    async def transcribe(self, audio_bytes: bytes, language: str = "es") -> str:
        if not audio_bytes:
            raise ValueError("No se recibió audio para transcribir.")
        # Determinístico y sin dependencias externas: útil para verificar
        # el contrato de la API (recibe audio, responde texto) en pruebas.
        return "[transcripción simulada] texto de prueba"
