# Módulo de IA (Fase 5 en curso)

El código del motor de reconocimiento de LSC vive en `backend/app/ai/lsc/`
(extracción de landmarks con MediaPipe + comparación DTW), no en esta
carpeta — esta carpeta está reservada para cuando el proyecto pase de
"comparación por plantillas" (DTW) a un modelo entrenado propiamente:

- `datasets/`      → Exportes de landmarks + etiquetas listos para entrenar.
- `preprocessing/` → Normalización/augmentación de secuencias de landmarks.
- `training/`       → Entrenamiento de un clasificador de secuencias
                       (LSTM/Transformer) una vez haya suficientes señas
                       reales publicadas y procesadas vía el panel admin.
- `evaluation/`     → Métricas: exactitud, precisión, recall, F1, latencia
                       (sección 28), comparando el modelo nuevo contra DTW.
- `models/`         → Modelos entrenados versionados (separados del código).
- `notebooks/`      → Exploración y experimentación.

El enfoque actual (DTW) no requiere entrenamiento y es apropiado para un
vocabulario pequeño (sección 28: no asumir que el primer modelo será
perfecto). Migrar a un modelo entrenado tiene sentido cuando el volumen de
señas y videos de referencia documentados crezca lo suficiente.
