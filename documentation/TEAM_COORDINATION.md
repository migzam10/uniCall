# 🤝 Sincronización del Equipo y Peticiones Cruzadas (Log de Desarrollo)

Este documento es nuestro espacio central para **notificar cambios importantes en la arquitectura, registrar avances clave y hacernos peticiones entre áreas**. 

Como somos 3 personas trabajando en áreas distintas, cada vez que alguien haga un cambio que afecte a otro, o necesite que otro desarrolle algo específico para poder avanzar, debe registrarlo aquí (y notificar en nuestro chat).

---

## 🧠 IA & Procesamiento LSC (Log y Peticiones)
**Desarrollador:** migzam
**Estado Actual:** Iniciando desarrollo de la Fase 6 (NLP) y estructurando pruebas para la Fase 8 (Calibración DTW).

### 📢 Notificación de Cambios (Lo que estoy haciendo)
* **[2026-09-24 22:50] Motor de Traducción y Endpoint Completados (Fase 6):** 
  He completado la integración del motor NLP con la base de datos y expuesto el endpoint para el Frontend.
  * Archivos modificados: `nlp_engine.py`, `lsc_data.py`, `lsc_recognition.py`.
  * **Nuevo Endpoint para Frontend:** `POST /api/v1/lsc/translate`.
  * **Contrato (Request):** `{"text": "Hola, yo quiero comer una manzana roja."}`
  * **Contrato (Response):** Devuelve la secuencia exacta para el Avatar 3D, indicando si la seña está validada en BD (`found_in_db`):
    ```json
    {
      "original_text": "Hola, yo quiero comer una manzana roja.",
      "sequence": [
        {"word": "HOLA", "sign_id": "uuid-1234", "found_in_db": true},
        {"word": "YO", "sign_id": null, "found_in_db": false},
        {"word": "QUERER", "sign_id": "uuid-5678", "found_in_db": true}
      ]
    }
    ```
* **[2026-09-24 22:00] Calibración de MediaPipe + DTW:** Estoy armando los scripts en `ai/evaluation/` para medir la distancia matemática de los movimientos y ajustar el umbral de precisión (`LSC_MAX_DTW_DISTANCE`).
* **[2026-09-24 23:30] Pipeline Machine Learning LSTM (Fase 8):** Creados scripts para construir dataset y entrenar un modelo LSTM dado que el DTW puro presenta superposición de distancias.

### 🎯 Peticiones al FRONTEND (Desarrollador 2)
1. **[CRÍTICO] MediaPipe en el Celular:** Para la inferencia en tiempo real (cuando la persona sorda hace señas a la cámara), enviar video en vivo al servidor es muy pesado y generará muchísima latencia. **Por favor investiga si puedes integrar MediaPipe Holistic directamente en Flutter** (existen paquetes como `google_mlkit_pose_detection` o integraciones nativas).
   * *Objetivo:* Que la app de Flutter extraiga los "landmarks" (coordenadas x,y,z del cuerpo y manos) localmente y me envíe **solo los números en formato JSON por WebSocket**. Si logras esto, nuestra latencia será casi cero. Si es imposible, me avisas para programar un buffer de video en el backend (plan B).
2. **Visor de Avatar 3D:** Empieza a investigar cómo cargar archivos `.glb` o `.gltf` en Flutter (ej. paquete `model_viewer_plus`). Yo te enviaré los identificadores de la animación desde el motor de NLP, y tú deberás poner a reproducir la animación en pantalla.

### 🎯 Peticiones al BACKEND (Desarrollador 1)
1. **Consultas a Base de Datos desde IA:** Para el motor NLP, voy a necesitar importar las dependencias o repositorios para hacer consultas a la tabla `LSCSign` y `LSCPhrase` y hacer *matching* con las palabras traducidas. Te aviso si necesito ayuda con el ORM de SQLAlchemy.
2. **Buffer de WebSockets:** Mantente alerta a la decisión del Frontend. Si el Frontend no logra procesar MediaPipe localmente, necesitaremos optimizar el `signaling_manager.py` para recibir un flujo constante de *frames* en base64 sin que colapse el *Event Loop* de FastAPI.

---

## 🌐 Frontend & Mobile (Log y Peticiones)
**Desarrollador:** Brandon
**Estado Actual:** Cubriendo Frontend + Backend/Arquitectura completos (Miguel se queda con IA/NLP). Arrancando la Fase 6 (Avatar 3D): rama `feature/avatar-3d-library`.

### 📢 Notificación de Cambios
* Respuesta a la petición #2 de Miguel: sí se va a integrar `model_viewer_plus` para el visor `.glb`/`.gltf` del avatar en la pantalla de videollamada.
* **[2026-10-16] Respuesta a la petición #1 (MediaPipe en el celular) — CERRADA, vamos por el Plan B:**
  Investigué el ecosistema real de paquetes Flutter para MediaPipe antes de decidir. Esto fue lo que encontré:
  * **No hay ningún paquete "Holistic" unificado para Flutter** (ni MediaPipe Tasks API de Google lo ofrece ya a nivel nativo — solo tareas separadas de pose y manos, habría que combinar dos).
  * Los dos candidatos reales:
    * `hand_landmarker` (manos, MediaPipe real vía JNI) → **solo Android**, 11 likes, 826 descargas.
    * `flutter_mp_pose_landmarker` (pose) → Android + iOS, pero el propio autor lo marca como **"initial support, still under testing"**, se instala vía git (no está publicado formal en pub.dev), un solo mantenedor, 6 likes.
  * **Ninguno de los dos soporta Web.** Nuestro README dice Android/iOS/Web — ir client-side nos obligaría a cortar Web de entrada.
  * Habría que correr dos plugins nativos de mantenedores distintos peleando por la misma cámara a la vez — combinación que nadie probó en producción.
  * Lo único rescatable: el formato de manos si es compatible (21 puntos x/y/z, mismo MediaPipe real), y casualmente tu LSTM ya sacó la cara del vector (`VECTOR_SIZE=258`), así que si esto madura algún día el formato ya calzaría.
  * **Decisión:** vamos por tu Plan B — la app manda fotogramas JPEG livianos por WebSocket a ~10fps, y el backend reusa el `VideoLandmarkExtractor` (Holistic completo) que ya está probado para reconocimiento de video grabado. Funciona igual en las 3 plataformas, sin apostarle a paquetes experimentales de un solo mantenedor. Documentado en README §5.2.
  * Si en el futuro el proyecto se reduce a "solo Android" o el equipo quiere invertir en integraciones nativas propias (no los paquetes comunitarios de hoy), vale la pena revisitar esto — queda como TODO explícito, no descartado para siempre.
  * Próximo paso de mi lado: definir el nuevo tipo de mensaje WebSocket para los frames (toca `signaling_client.dart` y `signaling.py`/`signaling_manager.py`) — lo arranco después de cerrar Fase 6.
* **[2026-10-16] Implementado reconocimiento de señas en vivo (Fase 7), rama `feature/fase7-live-sign-recognition`:**
  * Botón de "mantener presionado para señas" en la llamada (mismo patrón que el botón de voz). Mientras está presionado, manda fotogramas del video local por WebSocket (`sign-start`/`sign-frame`/`sign-stop`); al soltar, el backend corre DTW sobre lo acumulado (reusando `VideoLandmarkExtractor`/`dtw_distance`, nada nuevo del lado de IA) y le avisa al otro participante.
  * El resultado reconocido se inyecta directo en el flujo de subtítulos/avatar/TTS que ya existe — no hay UI nueva que mantener.
  * Ojo, Miguel: para que esto reconozca algo de verdad hace falta tener señas **publicadas con plantillas procesadas** en la BD (`process_video` de la Fase 5) — con la BD vacía siempre va a dar `matched: false`, que es el comportamiento correcto (nunca inventar), no un bug.
  * Probado end-to-end con un script manual (2 usuarios por WebSocket, frames sintéticos) — confirmado que el mensaje `sign-recognized` llega bien formado. Falta prueba en dispositivo real con cámara.

### 🎯 Peticiones a IA o Backend
* A Miguel: con esto tu petición #1 queda resuelta — nada bloqueante de tu lado, ya puedes asumir que el flujo de reconocimiento en vivo va a llegar por frames al backend, no por landmarks ya calculados desde el celular.

---

## ⚙️ Backend & Arquitectura (Log y Peticiones)
**Desarrollador:** Brandon
**Estado Actual:** Fase 6 (Biblioteca de Animaciones del Avatar) en curso, rama `feature/avatar-3d-library`.

### 📢 Notificación de Cambios
* **Nueva tabla `LSCAnimation`** (mismo patrón que `LSCVideo`): cada seña puede tener animaciones `.glb`/`.gltf` cargadas vía el panel admin (`POST/GET /api/v1/admin/lsc/signs/{sign_id}/animations`, `DELETE /api/v1/admin/lsc/animations/{id}`). `GET /api/v1/admin/lsc/signs/{id}` ahora también devuelve `animations` además de `videos`.
* **Nuevo contrato para `/api/v1/lsc/translate`** (Miguel, ojo con esto): la respuesta de tu `nlp_engine.py` se va a enriquecer con disponibilidad de animación antes de llegar al frontend. Ya armé `LSCDataService.enrich_translation_sequence(original_text, raw_sequence)` que toma tu output crudo (`[{"word", "sign_id", "found_in_db"}, ...]`) y agrega a cada item `has_animation: bool` y `animation_url: str | None`, más un `complete: bool` a nivel de toda la respuesta. **No lo conecté todavía a tu endpoint** porque tu rama `feature/fase6-nlp-engine` (PR #7) sigue sin mergear (bloqueado por el fix de spaCy que te comenté en el PR). En cuanto mergees, el cambio en `lsc_recognition.py` es de 3 líneas — avísame o hazlo tú mismo, está documentado en el código.
* Política de "nunca inventar" ya resuelta para el avatar: si una palabra no tiene seña o no tiene animación cargada, el frontend muestra solo el subtítulo de esa palabra (nunca un avatar inventado), y si falta cualquiera en la frase completa se marca `complete=false` para avisar que la traducción quedó incompleta.

### 🎯 Peticiones a Frontend o IA
* A Miguel: revisa el punto de arriba sobre `/translate` cuando retomes el PR #7. Ya quedó integrado en este último merge.
