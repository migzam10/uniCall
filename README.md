# DOCUMENTO MAESTRO DE DESARROLLO Y CONTINUIDAD
## Plataforma de Videollamadas Accesibles con Traducción LSC ⇄ Español

Este documento está diseñado para que cualquier desarrollador o Inteligencia Artificial asuma el control del proyecto, entienda su propósito, conozca el estado actual del código y tenga un mapa de ruta exacto sobre **qué falta por hacer y cómo debe programarse**.

---

## 1. ¿QUÉ ES EL PROYECTO? (Visión General)
Es una aplicación multiplataforma (Android, iOS, Web) de videollamadas enfocada en la comunicación bidireccional en tiempo real entre personas sordas y oyentes utilizando la **Lengua de Señas Colombiana (LSC)**.

**El flujo bidireccional es el núcleo del sistema:**
1. **Persona Oyente:** Habla (Voz) → IA transcribe (STT) a texto → IA traduce lingüísticamente a LSC → Avatar 3D reproduce señas → Persona Sorda.
2. **Persona Sorda:** Realiza señas a la cámara → IA captura movimiento (Computer Vision) → Reconoce secuencias de señas → Traduce a texto en Español → IA sintetiza voz (TTS) → Persona Oyente.

**Stack Tecnológico Base:**
*   **Frontend:** Flutter + Dart (con `flutter_webrtc`).
*   **Backend:** Python + FastAPI + WebSockets + SQLAlchemy (PostgreSQL/SQLite).
*   **IA & Procesamiento:** MediaPipe Holistic (Landmarks offline), algoritmos DTW (Dynamic Time Warping), `faster-whisper` (STT), `espeak-ng` (TTS).
*   **Infraestructura:** Docker, WebRTC (STUN/TURN para señalización peer-to-peer).

---

## 2. ¿QUÉ ESTÁ HECHO YA? (Estado Actual: Fases 1 a 5 Completadas)

El repositorio actual cuenta con una base sólida y funcional que abarca la arquitectura, comunicación peer-to-peer y los primeros modelos de IA. 

### Backend (Python/FastAPI)
*   **Autenticación y Usuarios (Fase 1):** Sistema JWT, roles (`oyente`, `sordo`, `administrador`), perfiles y preferencias.
*   **Señalización y Llamadas (Fase 2):** Gestión de contactos, generación de códigos únicos para videollamadas, e intercambio de *offer/answer/ICE candidates* por WebSockets (`/ws/calls/{call_id}`).
*   **Audio y Texto (Fase 3):** Capa de abstracción modular. Síntesis de voz funcional con `espeak-ng` (masculina/femenina) y reconocimiento de voz intercambiable (Mock para pruebas, o Whisper real). Soporte para subtítulos compartidos en vivo mediante WebSocket.
*   **Gestión de Datos LSC (Fase 4):** Panel de administración (API) para crear categorías, señas, subir videos (mp4/webm) y construir secuencias de frases (borrador vs publicado).
*   **IA de Reconocimiento LSC Inicial (Fase 5):** Motor de extracción de *landmarks* 100% offline usando **MediaPipe Holistic** (rostro, manos, cuerpo). Algoritmo de comparación por **DTW (Dynamic Time Warping)**. El sistema ya procesa videos para crear "plantillas" y evalúa si un video entrante coincide midiendo distancias.

### Frontend (Flutter)
*   **UI/UX (Fases 1 y 2):** Pantallas accesibles (Splash, Login, Registro, Contactos, Perfil). Pantalla de videollamada funcional con WebRTC (cámara y controles). Motor `CallEngine` para la señalización.
*   **Integración de Audio y Texto (Fase 3):** Botón "mantener para hablar", overlays de subtítulos en pantalla y reproducción de TTS de los mensajes recibidos.
*   **Panel Admin (Fases 4 y 5):** UI para que los administradores suban videos, gestionen el vocabulario LSC y procesen los videos en plantillas de *landmarks*.

**⚠️ CUIDADO FRONTEND:** El código actual de Flutter no contiene las carpetas nativas (`android/`, `ios/`, `web/`). Es obligatorio ejecutar `flutter create . --platforms=android,ios,web` antes de cualquier compilación e inyectar los permisos de cámara y micrófono (ver `webrtc-permissions.md`).

---

## 3. ¿QUÉ SE VA A HACER? (Próximos Pasos)

Faltan las **Fases 6, 7 y 8**. El objetivo es conectar el reconocimiento que ya existe y añadir la generación del Avatar 3D para completar el ciclo de traducción.

*   **FASE 6:** Implementar la Biblioteca de Animaciones y el Avatar 3D.
*   **FASE 7:** Integración Total Bidireccional en la Videollamada (WebRTC + IA completa).
*   **FASE 8:** Pruebas exhaustivas, calibración empírica del DTW con señas reales y despliegue.

---

## 4. ¿CÓMO SE HARÁ? (Guía de Programación e Implementación)

A continuación, se detalla cómo la IA o el programador debe abordar el código faltante, manteniendo la filosofía modular actual.

### Implementación de la Fase 6: Avatar 3D y Traducción (Texto → LSC)
1.  **Frontend (Flutter - Avatar):** 
    *   No programes un motor 3D desde cero. Integra visualizadores de modelos ligeros (como `.glb` o `.gltf`) usando paquetes como `model_viewer_plus` o `flutter_3d_controller`.
    *   La UI debe superponer el Avatar 3D (cuando esté activo) en la pantalla de la videollamada para el usuario sordo.
2.  **Backend (Python - NLP a Señas):**
    *   Desarrollar un módulo en `app/ai/translation/` que reciba el texto (ej. "Buenos días, ¿cómo estás?").
    *   Realizar un procesamiento lingüístico simple (NLP) que omita artículos innecesarios y adapte la sintaxis al LSC (ej. "DÍA BUENO, TÚ CÓMO").
    *   Mapear las palabras resultantes a IDs de animaciones de la Base de Datos (`LSCAnimations`).
3.  **Biblioteca de Animaciones (Backend):**
    *   Añadir modelos de base de datos para almacenar metadata de animaciones 3D.
    *   El endpoint debe devolver la secuencia de archivos `.glb` o identificadores de animación que el cliente Flutter debe reproducir secuencialmente.

### Implementación de la Fase 7: Integración en la Videollamada
1.  **Orquestación Frontend (`CallEngine`):**
    *   **Canal Sordo → Oyente:** Capturar frames del video local con WebRTC. Enviar fragmentos (o *landmarks* ya extraídos) al endpoint de reconocimiento `/api/v1/lsc/recognize`. Recibir el ID de la seña. Mapear a texto. Enviar comando de síntesis al TTS local (o backend).
    *   **Canal Oyente → Sordo:** Capturar audio del micrófono. Usar el STT (que ya está integrado en la Fase 3). Enviar texto al backend para recibir secuencia LSC. Reproducir secuencia en el Avatar 3D local.
2.  **Optimización de Latencia:**
    *   No enviar video crudo si no es necesario. Modificar el cliente Flutter para que corra MediaPipe (mediante un *plugin* nativo) y envíe **solamente** las coordenadas (*landmarks*) por WebSockets al servidor de IA para el algoritmo DTW. Si esto es muy complejo en Dart, enviar fotogramas ligeros (JPEG en base64) por WebSocket al backend, pero controlando el *framerate* (ej. 10 fps).

### Implementación de la Fase 8: Pruebas y Calibración
1.  **Calibración del Modelo DTW (¡CRÍTICO!):** 
    *   Actualmente el umbral `LSC_MAX_DTW_DISTANCE` es teórico porque no se probó con humanos reales haciendo señas (debido a limitaciones del entorno). Se DEBE crear un script Python en la carpeta `ai/evaluation/` que consuma un lote de videos reales cargados, compare distancias intrasujeto vs intersujeto y ajuste el umbral.
2.  **Performance:**
    *   Asegurar que el loop asíncrono de FastAPI (`asyncio`) no se bloquee durante la comparación DTW (usar `run_in_threadpool` si las matrices son enormes).

---

## 5. DECISIONES PENDIENTES ANTES DE EMPEZAR LA FASE 6

Al reconstruir la especificación original perdida (ver `documentation/ESPECIFICACION_RECONSTRUIDA.md`), quedó claro que las Fases 1 a 5 tuvieron un nivel de detalle (más de 30 secciones) que las Fases 6, 7 y 8 todavía no tienen — hoy son 2-3 frases cada una. Antes de escribir código de estas fases, el equipo debe resolver y dejar documentadas aquí las siguientes decisiones, con el mismo rigor que se usó para elegir STT/TTS/DTW.

### 5.1 Fase 6 (Avatar): falta el checklist que sí se usó para STT/TTS/DTW
*   **Formato/rig del modelo 3D:** confirmar que `model_viewer_plus` / `flutter_3d_controller` soportan el esqueleto elegido antes de generar o comprar animaciones sobre él.
*   **Transición entre animaciones consecutivas de una frase:** ¿corte seco o interpolación (blend)? Afecta directamente la naturalidad, que es la prioridad #4 definida en la especificación (precisión del movimiento > claridad de las señas > sincronización > naturalidad > rendimiento).
*   **Qué hacer cuando una palabra de la frase NO tiene animación documentada:** en línea con la regla de "nunca inventar" (Sección 29 de la especificación reconstruida), decidir explícitamente entre (a) omitir la palabra, (b) mostrar solo el subtítulo de esa palabra sin animación, o (c) avisar que la traducción está incompleta. No dejarlo implícito en el código de quien lo programe.

### 5.2 Fase 7 (Integración): hay una decisión arquitectónica pendiente, no una nota al margen
El punto 2 de la implementación de Fase 7 dice literalmente "si esto es muy complejo en Dart, enviar fotogramas" — eso es en realidad una decisión de arquitectura (extracción de landmarks *client-side* en Flutter vs. *server-side* en el backend) que cambia la latencia, el costo de servidor y el contrato del WebSocket. Debe decidirse y documentarse **antes** de escribir el código de esta fase, no resolverse como fallback improvisado a mitad de desarrollo.

### 5.3 Fase 8 (Calibración): falta una definición de "terminado"
"Calibrar el umbral `LSC_MAX_DTW_DISTANCE`" no es una tarea con fin claro sin un criterio numérico. Antes de escribir el script de `ai/evaluation/`, definir aquí qué métrica y qué valor mínimo se considera aceptable (ej. recall/precisión/F1 sobre el vocabulario piloto — ver Sección 28 de la especificación reconstruida). Sin esto, la fase nunca tiene un "listo" objetivo.

### 5.4 Transversal: manejo de fallos (no está cubierto en ninguna fase actual)
Ninguna fase documenta qué debe pasar cuando algo falla a mitad de una llamada. Para una aplicación de accesibilidad esto no es un detalle secundario — es parte del producto. Como mínimo, documentar el comportamiento esperado ante:
*   Caída de la conexión a internet durante la llamada.
*   La cámara pierde de vista la seña (mala iluminación, mano fuera de cuadro) a mitad de una frase.
*   El backend de reconocimiento/traducción no responde o tarda demasiado.

---

## 6. REGLAS ESTRICTAS DE DESARROLLO

*   **Nunca modifiques la arquitectura base para hacer atajos.** La abstracción `AI Engine` (STT, TTS, Visión) debe mantenerse para poder cambiar modelos a futuro.
*   **Separar Entornos:** El entrenamiento/procesamiento de video es asíncrono y separado de la inferencia en tiempo real. 
*   **Validación de LSC:** Nunca programes "diccionarios palabra a palabra" estáticos. La base de datos debe guiar el mapeo semántico.
*   **Seguridad:** Sigue utilizando las variables del `.env`. No subas claves JWT al repositorio.
*   **Flujo de Trabajo Git y Ramas (¡ESTRICTO!):**
    *   La rama `main` es **sagrada**: siempre debe estar funcional y estable. **NUNCA SE TRABAJA DIRECTAMENTE EN MAIN**.
    *   Cada vez que se vaya a desarrollar algo nuevo o corregir algo, se debe crear una rama nueva a partir de `main` con la siguiente nomenclatura:
        *   Funciones nuevas: `feature/nombre-de-tarea` (ej. `feature/avatar-3d`)
        *   Corrección de errores: `fix/descripcion-bug` (ej. `fix/error-login`)
    *   Cualquier desarrollador (o IA que genere código) debe aislar su trabajo en su respectiva rama y hacer los commits ahí.
    *   Al terminar la tarea, la rama se publica para hacer pruebas de integración. Solo cuando el equipo valide que el código nuevo no rompe nada, se aprobará la unión (merge) con `main`, que será la versión estable oficial.
*   **Convención de Commits:** Los mensajes deben ser descriptivos y seguir esta estructura:
    *   `feat:` para funcionalidades nuevas (ej. `feat: agrego boton de logo`).
    *   `fix:` para correcciones de errores (ej. `fix: arreglo error de login`).
    *   `docs:` si se edita documentación (ej. `docs: actualizo readme`).
    *   *(Antes de hacer merge, se exige correr las pruebas automatizadas `cd backend && ./test_manual.sh` para no subir nada roto).*