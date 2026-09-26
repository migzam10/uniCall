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
**Desarrollador:** [Nombre del encargado de Flutter]
**Estado Actual:** [Pendiente de actualizar]

### 📢 Notificación de Cambios
* *(Escribe aquí tus cambios cuando inicies tu trabajo)*

### 🎯 Peticiones a IA o Backend
* *(Escribe aquí qué necesitas que te preparemos)*

---

## ⚙️ Backend & Arquitectura (Log y Peticiones)
**Desarrollador:** [Nombre del encargado de Python/BD]
**Estado Actual:** [Pendiente de actualizar]

### 📢 Notificación de Cambios
* *(Escribe aquí tus cambios cuando inicies tu trabajo)*

### 🎯 Peticiones a Frontend o IA
* *(Escribe aquí qué necesitas que te preparemos)*
