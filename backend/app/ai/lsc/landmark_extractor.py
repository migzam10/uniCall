"""
Extracción de landmarks corporales con MediaPipe Holistic.

Decisión documentada (sección 24):
- Precisión: buena para un modelo genérico de pose/manos/rostro (no
  entrenado específicamente en LSC, pero es el insumo estándar de la
  industria para luego construir un clasificador de secuencias sobre él).
- Latencia: ~60-70ms por frame en CPU sin GPU (medido en este entorno);
  suficiente para procesar clips cortos, mejorable con GPU en producción.
- Disponibilidad: corre 100% offline con `model_complexity=1`, cuyo peso
  viene empaquetado en la librería — no depende de descargar nada en
  tiempo de ejecución (a diferencia de otras opciones de MediaPipe que
  requieren descargar un archivo .task desde servidores de Google).
- Recursos de servidor: moderados en CPU, sin necesidad de GPU para un MVP.
- Licencia: Apache 2.0.
- Integración: directa vía pip.
- Escalabilidad: el extractor de landmarks se puede mover a un servicio de
  IA separado (sección 26) y escalar horizontalmente si el volumen crece.

Sección 10: no se limita a las manos — se capturan también pose corporal y
rostro, y el resultado es una secuencia (un vector por frame), no un
snapshot único.
"""
import cv2
import numpy as np

# Import perezoso de mediapipe: solo se paga el costo de cargar el modelo
# cuando realmente se usa este extractor.
_holistic_module = None


def _get_holistic_module():
    global _holistic_module
    if _holistic_module is None:
        import mediapipe as mp

        _holistic_module = mp.solutions.holistic
    return _holistic_module


POSE_LANDMARKS = 33
HAND_LANDMARKS = 21
FACE_LANDMARKS = 468

# Por landmark: x, y, z (+ visibility solo en pose)
FRAME_VECTOR_SIZE = POSE_LANDMARKS * 4 + HAND_LANDMARKS * 3 * 2 + FACE_LANDMARKS * 3


def _landmarks_to_array(landmark_list, with_visibility: bool, count: int) -> np.ndarray:
    if landmark_list is None:
        width = 4 if with_visibility else 3
        return np.zeros(count * width, dtype=np.float32)

    values = []
    for lm in landmark_list.landmark:
        values.extend([lm.x, lm.y, lm.z])
        if with_visibility:
            values.append(lm.visibility)
    return np.array(values, dtype=np.float32)


def extract_frame_vector(results) -> np.ndarray:
    """Convierte un resultado de Holistic en un único vector plano."""
    pose = _landmarks_to_array(results.pose_landmarks, with_visibility=True, count=POSE_LANDMARKS)
    left_hand = _landmarks_to_array(results.left_hand_landmarks, with_visibility=False, count=HAND_LANDMARKS)
    right_hand = _landmarks_to_array(results.right_hand_landmarks, with_visibility=False, count=HAND_LANDMARKS)
    face = _landmarks_to_array(results.face_landmarks, with_visibility=False, count=FACE_LANDMARKS)
    return np.concatenate([pose, left_hand, right_hand, face])


def has_hand_detection(results) -> bool:
    return results.left_hand_landmarks is not None or results.right_hand_landmarks is not None


class VideoLandmarkExtractor:
    """
    Extrae una secuencia de vectores de landmarks a partir de un archivo
    de video, muestreando a una tasa de frames objetivo para mantener el
    costo de cómputo acotado (sección 25: rendimiento).
    """

    def __init__(self, target_fps: float = 8.0, max_frames: int = 90):
        self.target_fps = target_fps
        self.max_frames = max_frames

    def extract_from_file(self, video_path: str) -> tuple[list[list[float]], int]:
        """
        Devuelve (secuencia_de_vectores, frames_con_mano_detectada).

        La secuencia puede estar vacía si el video no se pudo leer.
        """
        holistic_module = _get_holistic_module()
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return [], 0

        source_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_interval = max(1, round(source_fps / self.target_fps))

        sequence: list[list[float]] = []
        hand_frames = 0
        frame_index = 0

        with holistic_module.Holistic(static_image_mode=False, model_complexity=1) as holistic:
            while len(sequence) < self.max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_index % frame_interval == 0:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = holistic.process(rgb_frame)
                    sequence.append(extract_frame_vector(results).tolist())
                    if has_hand_detection(results):
                        hand_frames += 1

                frame_index += 1

        cap.release()
        return sequence, hand_frames
