"""
Reconocimiento de señas en vivo, frame por frame, durante una videollamada
(Fase 7).

A diferencia de `VideoLandmarkExtractor` (que abre y cierra un `Holistic`
por cada archivo de video completo), aquí la persona hace señas durante
varios segundos mientras llegan fotogramas sueltos por WebSocket — se
necesita UN `Holistic` persistente que viva mientras dure la captura
("mantener presionado para señas"), no uno por frame ni uno por archivo.
"""
import cv2
import numpy as np

from app.ai.lsc.landmark_extractor import (
    _get_holistic_module,
    extract_frame_vector,
    has_hand_detection,
)


class LiveSignRecognizer:
    """
    Una instancia por intento de seña en vivo: se crea al recibir
    "sign-start", recibe frames vía `process_frame()` mientras el usuario
    mantiene presionado el botón, y se cierra con `finish()` al soltar
    ("sign-stop"), devolviendo la secuencia acumulada lista para DTW.
    """

    def __init__(self, max_frames: int = 90):
        self.max_frames = max_frames
        self._sequence: list[list[float]] = []
        self._hand_frames = 0
        holistic_module = _get_holistic_module()
        self._holistic = holistic_module.Holistic(static_image_mode=False, model_complexity=1)

    def process_frame(self, image_bytes: bytes) -> None:
        """Decodifica un frame (PNG/JPEG) y lo agrega a la secuencia, si no se alcanzó el límite."""
        if len(self._sequence) >= self.max_frames:
            return

        buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        if frame is None:
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._holistic.process(rgb_frame)
        self._sequence.append(extract_frame_vector(results).tolist())
        if has_hand_detection(results):
            self._hand_frames += 1

    def finish(self) -> tuple[list[list[float]], int]:
        """Cierra el `Holistic` y devuelve (secuencia, frames_con_mano_detectada)."""
        self._holistic.close()
        return self._sequence, self._hand_frames
