# 🤝 Sincronización del Equipo y Peticiones Cruzadas (Log de Desarrollo)

Este documento es nuestro espacio central para **notificar cambios importantes en la arquitectura, registrar avances clave y hacernos peticiones entre áreas**. 

Como somos 3 personas trabajando en áreas distintas, cada vez que alguien haga un cambio que afecte a otro, o necesite que otro desarrolle algo específico para poder avanzar, debe registrarlo aquí (y notificar en nuestro chat).

---

## 🧠 IA & Procesamiento LSC (Log y Peticiones)
**Desarrollador:** migzam
**Estado Actual:** Iniciando desarrollo de la Fase 6 (NLP) y estructurando pruebas para la Fase 8 (Calibración DTW).

### 📢 Notificación de Cambios (Lo que estoy haciendo)
* **Motor de Traducción (NLP):** Estoy construyendo el motor en `backend/app/ai/translation/nlp_engine.py`. Este motor recibirá el texto en español hablado por la persona oyente, eliminará *stop-words* (artículos, preposiciones) y adaptará la gramática para que devuelva una lista de palabras/IDs compatibles con la base de datos de LSC.
* **Calibración de MediaPipe + DTW:** Estoy armando los scripts en `ai/evaluation/` para medir la distancia matemática de los movimientos y ajustar el umbral de precisión (`LSC_MAX_DTW_DISTANCE`).

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
* Todavía sin resolver la petición #1 (MediaPipe client-side en Flutter) — es la decisión de arquitectura de Fase 7, se aborda después de cerrar la Fase 6.

### 🎯 Peticiones a IA o Backend
* Ninguna por ahora.

---

## ⚙️ Backend & Arquitectura (Log y Peticiones)
**Desarrollador:** Brandon
**Estado Actual:** Fase 6 (Biblioteca de Animaciones del Avatar) en curso, rama `feature/avatar-3d-library`.

### 📢 Notificación de Cambios
* **Nueva tabla `LSCAnimation`** (mismo patrón que `LSCVideo`): cada seña puede tener animaciones `.glb`/`.gltf` cargadas vía el panel admin (`POST/GET /api/v1/admin/lsc/signs/{sign_id}/animations`, `DELETE /api/v1/admin/lsc/animations/{id}`). `GET /api/v1/admin/lsc/signs/{id}` ahora también devuelve `animations` además de `videos`.
* **Nuevo contrato para `/api/v1/lsc/translate`** (Miguel, ojo con esto): la respuesta de tu `nlp_engine.py` se va a enriquecer con disponibilidad de animación antes de llegar al frontend. Ya armé `LSCDataService.enrich_translation_sequence(original_text, raw_sequence)` que toma tu output crudo (`[{"word", "sign_id", "found_in_db"}, ...]`) y agrega a cada item `has_animation: bool` y `animation_url: str | None`, más un `complete: bool` a nivel de toda la respuesta. **No lo conecté todavía a tu endpoint** porque tu rama `feature/fase6-nlp-engine` (PR #7) sigue sin mergear (bloqueado por el fix de spaCy que te comenté en el PR). En cuanto mergees, el cambio en `lsc_recognition.py` es de 3 líneas — avísame o hazlo tú mismo, está documentado en el código.
* Política de "nunca inventar" ya resuelta para el avatar: si una palabra no tiene seña o no tiene animación cargada, el frontend muestra solo el subtítulo de esa palabra (nunca un avatar inventado), y si falta cualquiera en la frase completa se marca `complete=false` para avisar que la traducción quedó incompleta.

### 🎯 Peticiones a Frontend o IA
* A Miguel: revisa el punto de arriba sobre `/translate` cuando retomes el PR #7.
