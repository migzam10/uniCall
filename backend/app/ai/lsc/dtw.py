"""
Dynamic Time Warping (DTW) para comparar dos secuencias de landmarks de
distinta duración (sección 10: el reconocimiento debe procesar secuencias
de señas, considerando la temporalidad del movimiento).

Se elige DTW como enfoque del modelo inicial (en vez de una red neuronal
entrenada) porque:
- No requiere un conjunto de entrenamiento grande: compara directamente
  contra los videos de referencia documentados y cargados en la Fase 4.
- Es interpretable: la distancia resultante tiene un significado claro
  (qué tan parecidos son los movimientos en el tiempo).
- Es apropiado para un primer modelo con vocabulario pequeño, en línea con
  la sección 28: "no considerar que el primer modelo será perfecto" y con
  la sección 33: empezar simple antes de invertir en entrenamiento pesado.

Limitación explícita: no generaliza tan bien como un modelo entrenado con
muchos ejemplos por seña. Está pensado como punto de partida, reemplazable
por un clasificador de secuencias (LSTM/Transformer) en `ai/training/`
cuando exista suficiente material validado.
"""
import numpy as np


def dtw_distance(seq_a: list[list[float]], seq_b: list[list[float]]) -> float:
    """
    Distancia DTW normalizada por longitud entre dos secuencias de
    vectores. Complejidad O(n*m); adecuado para clips cortos (decenas de
    frames, no miles).
    """
    a = np.asarray(seq_a, dtype=np.float32)
    b = np.asarray(seq_b, dtype=np.float32)
    n, m = len(a), len(b)

    if n == 0 or m == 0:
        return float("inf")

    cost = np.full((n + 1, m + 1), np.inf, dtype=np.float64)
    cost[0, 0] = 0.0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            point_dist = float(np.linalg.norm(a[i - 1] - b[j - 1]))
            cost[i, j] = point_dist + min(cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1])

    # Normalizado por el largo del camino de alineación (aprox. n+m) para
    # que clips de distinta duración sean comparables entre sí.
    return cost[n, m] / (n + m)
