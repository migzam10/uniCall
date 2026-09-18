"""
Síntesis de voz usando espeak-ng.

Decisión documentada (sección 24 — no elegir tecnología solo por
popularidad):
- Precisión/naturalidad: básica (voz robótica, típica de síntesis por
  formantes), inferior a motores neuronales como Piper o Coqui TTS.
- Latencia: excelente, genera audio en milisegundos, sin GPU.
- Disponibilidad: se instala como paquete del sistema (espeak-ng), sin
  descargar modelos ni depender de servicios externos.
- Recursos de servidor: mínimos (CPU, sin GPU).
- Entrenamiento: no aplica (motor basado en reglas, no en modelos entrenados).
- Licencia: GPL, sin costo.
- Integración: trivial (llamada a binario del sistema).
- Escalabilidad: alta, al no requerir GPU ni modelos pesados en memoria.

Se elige como motor por defecto para tener síntesis de voz funcional desde
el primer día. La arquitectura (interfaz SpeechSynthesizer) permite
reemplazarlo por un motor neuronal con voces más naturales (p. ej. Piper o
Coqui TTS) en una fase posterior sin tocar el resto de la aplicación.
"""
import asyncio
import tempfile
from pathlib import Path

from app.ai.base import SpeechSynthesizer

# Variante de voz de espeak-ng por idioma/preferencia. "es-419" es español
# latinoamericano (más cercano al español colombiano que "es" de España).
_VOICE_MAP = {
    "masculina": "es-419",
    "femenina": "es-419+f3",
}


class EspeakSynthesizer(SpeechSynthesizer):
    async def synthesize(self, text: str, voice: str, language: str = "es") -> bytes:
        if not text.strip():
            raise ValueError("El texto a sintetizar no puede estar vacío.")

        espeak_voice = _VOICE_MAP.get(voice, _VOICE_MAP["femenina"])

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "output.wav"
            process = await asyncio.create_subprocess_exec(
                "espeak-ng",
                "-v", espeak_voice,
                "-s", "160",  # velocidad de habla (palabras por minuto)
                "-w", str(output_path),
                text,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await process.communicate()

            if process.returncode != 0:
                raise RuntimeError(f"espeak-ng falló: {stderr.decode(errors='ignore')}")

            return output_path.read_bytes()
