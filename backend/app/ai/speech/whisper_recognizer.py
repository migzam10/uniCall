"""
Reconocimiento de voz usando faster-whisper (reimplementación optimizada
de OpenAI Whisper sobre CTranslate2).

Decisión documentada (sección 24):
- Precisión: alta, incluso en el modelo "small"/"medium" para español.
- Latencia: buena en CPU con el modelo "small" (aceptable para casi tiempo
  real); mucho mejor con GPU.
- Disponibilidad: corre localmente, no depende de un servicio externo de
  pago ni de conexión a internet en producción (solo la primera vez, para
  descargar los pesos del modelo).
- Recursos de servidor: moderados en CPU con modelos pequeños; se
  beneficia de GPU si está disponible.
- Entrenamiento: no se reentrena directamente, pero es robusto out-of-the-box
  para español.
- Licencia: MIT (el código); los pesos de Whisper son de uso abierto.
- Integración: sencilla vía pip, sin dependencias de servicios cloud.
- Escalabilidad: se puede desplegar como servicio de IA separado
  (sección 26) y escalar horizontalmente.

El modelo se carga de forma perezosa (lazy) y se cachea en memoria para no
pagar el costo de carga en cada transcripción.
"""
import asyncio
import tempfile
from pathlib import Path
from typing import ClassVar

from app.ai.base import SpeechRecognizer


class WhisperRecognizer(SpeechRecognizer):
    _model: ClassVar = None
    _model_size: ClassVar[str] = "small"

    def _get_model(self):
        if WhisperRecognizer._model is None:
            # Import perezoso: solo se paga el costo (y la dependencia de
            # los pesos del modelo) cuando realmente se usa este motor.
            from faster_whisper import WhisperModel

            WhisperRecognizer._model = WhisperModel(
                WhisperRecognizer._model_size, device="cpu", compute_type="int8"
            )
        return WhisperRecognizer._model

    async def transcribe(self, audio_bytes: bytes, language: str = "es") -> str:
        return await asyncio.to_thread(self._transcribe_sync, audio_bytes, language)

    def _transcribe_sync(self, audio_bytes: bytes, language: str) -> str:
        model = self._get_model()
        with tempfile.TemporaryDirectory() as tmp_dir:
            audio_path = Path(tmp_dir) / "input.wav"
            audio_path.write_bytes(audio_bytes)
            segments, _info = model.transcribe(str(audio_path), language=language)
            return " ".join(segment.text.strip() for segment in segments).strip()
