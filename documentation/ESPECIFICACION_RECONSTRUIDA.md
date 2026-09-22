# Especificación original — Reconstrucción a partir del código

## Cómo se hizo este documento (léase antes de usar)

El equipo perdió el documento de especificación original ("el prompt experto")
que se usó para generar el código de las Fases 1-5. El `README.md` de la raíz
es un **resumen posterior**, no la especificación misma — tiene solo 5
secciones numeradas, pero el código fuente cita **"sección N de la
especificación"** en docstrings y comentarios hasta la **sección 33**.

Este documento reconstruye lo que se puede probar que decía cada sección,
citando el archivo y la línea exacta de donde sale cada afirmación. Es una
reconstrucción **parcial por diseño**: solo cubre lo que quedó como rastro en
el código. Cualquier matiz, ejemplo o justificación más larga que no se haya
plasmado en un comentario está perdido para siempre.

**Antes de tratar esto como la especificación real:** pregunten a los 3 si
alguien tiene el documento original en un chat de ChatGPT/Claude, un Google
Doc, Notion, o similar — reconstruir desde comentarios de código es el último
recurso, no el primero. Este archivo es ese último recurso, ya ejecutado.

**Convención usada abajo:**
- 🟢 **Evidencia directa** — cita textual o paráfrasis muy cercana de un comentario real.
- 🟡 **Inferencia** — se puede deducir del contexto/implementación, pero no hay una frase explícita.
- ⚪ **Hueco** — número de sección mencionado en otro lugar pero sin ningún rastro de contenido.

---

## Secciones reconstruidas

### Sección 1 — Visión general del producto ⚪
Sin rastro directo en código. Cubierto de forma general por el README actual
(sección "¿Qué es el proyecto?"): plataforma de videollamadas bidireccional
oyente ⇄ sordo con traducción LSC ⇄ español.

### Sección 2 — Arquitectura WebRTC: servidor no debe ser cuello de botella 🟢
> "no convertir al servidor en un intermediario innecesario de todo el
> tráfico audiovisual"
— `backend/app/websocket/signaling_manager.py:8`, replicado en
`frontend/flutter_app/lib/services/call_engine.dart:19`

El servidor **solo coordina señalización** (offer/answer/ICE candidates).
El audio/video viaja directo entre los dos peers vía WebRTC P2P — nunca pasa
por el servidor.

### Sección 3 — Tipos de cuenta 🟢
> "oyente, sordo, administrador"
— `backend/app/models/user.py:46`, replicado en
`frontend/flutter_app/lib/models/user_role.dart:1`

Tres roles de usuario, sin más granularidad mencionada (no hay p. ej. rol de
"intérprete" o "moderador").

### Sección 4 — Preferencias de comunicación al registro 🟢
> "Preferencias de comunicación (definidas en el registro, sección 4)"
— `backend/app/models/user_preferences.py:22`

Cada usuario nuevo define, desde el registro: idioma preferido
(`preferred_language`, default `es-CO`) y lengua de señas (`sign_language`,
default `LSC`). Cada usuario obtiene automáticamente un `Profile` y
`UserPreferences` por defecto al crearse (ver también sección 20).

### Sección 5 — Videollamada directa a un contacto 🟢
> "iniciar videollamada directamente" (a un contacto ya agregado),
> independiente de compartir el código manualmente
— `backend/app/models/call_invitation.py:2-3`, `backend/app/api/calls.py:31`

Dos formas de iniciar llamada conviven: por código compartido (sección 6) y
por invitación directa a un contacto ya agregado.

### Sección 6 — Llamada por código/enlace 🟢
> "Crea una llamada y genera un código/enlace de invitación"
— `backend/app/api/calls.py:23`

### Sección 7 — ⚪
Sin rastro. Por posición (entre "iniciar llamada" y "STT"), podría cubrir
gestión de contactos (agregar/aceptar/rechazar) — hay código para esto
(`ContactRequest`) pero ningún comentario lo ata explícitamente a esta
sección.

### Sección 8 — Flujo oyente→sordo, tramo 1: voz→texto 🟢
> "Español hablado -> texto (sección 8, primer tramo del flujo)"
— `backend/app/api/speech.py:14`, replicado en
`frontend/flutter_app/lib/features/calls/call_screen.dart:20`

Primer tramo del flujo bidireccional descrito en el README (persona oyente
habla → STT → texto). Grabar mientras se mantiene presionado un botón,
transcribir al soltar.

### Sección 9 — Flujo bidireccional completo LSC⇄español 🟢
Dos citas complementarias:
> "LSC -> texto (sección 9, primer tramo)" — `backend/app/api/lsc_recognition.py:10`
> "Texto -> voz (sección 9, último tramo del flujo LSC -> español)" — `backend/app/api/speech.py:15`

Cubre el flujo persona sorda → persona oyente completo: seña → texto (primer
tramo) → voz (tramo final). Es el "espejo" del flujo de la sección 8.

### Sección 10 — Requisitos del reconocimiento de señas 🟢
Tres citas:
> "el reconocimiento debe procesar secuencias de señas, considerando la temporalidad del movimiento" — `backend/app/ai/lsc/dtw.py:3`
> "no se limita a las manos — se capturan también pose corporal y rostro, y el resultado es una secuencia (un vector por frame), no un snapshot único" — `backend/app/ai/lsc/landmark_extractor.py:20`
> "el reconocimiento trabaja con secuencias, no solo señas individuales" — `backend/app/models/lsc_phrase.py:12`

Requisito explícito: el reconocimiento NUNCA es de un frame estático — siempre
secuencias temporales, y captura cuerpo completo (pose + ambas manos + rostro),
no solo manos.

### Sección 11 — Árbol de contenido LSC 🟢
> "Categoría del árbol de contenido LSC (sección 11), por ejemplo: saludos,
> personas, lugares, acciones, objetos, alimentos, emociones"
— `backend/app/models/lsc_category.py:9-10`

También cubre los videos de referencia como "material visual documentado"
(`backend/app/models/lsc_video.py:9`).

### Sección 12 — Separación dato crudo vs. dato derivado + control de calidad 🟢
Múltiples citas convergentes:
> "no promover contenido a producción sin un proceso de revisión" — `backend/app/models/lsc_sign.py:24`
> "dataset de entrenamiento separado del video crudo" — `backend/app/services/lsc_recognition_service.py:17`
> "el dato crudo (video) del dato derivado usado por el modelo (plantilla de landmarks)" — `backend/app/models/lsc_sign_template.py:9`
> "versionar cuando sea necesario" — `backend/app/schemas/lsc_data.py:41`
> "Acción explícita, separada de la carga del video" — `backend/app/api/lsc_data.py:32`

Regla central: **cargar un video ≠ procesarlo ≠ publicarlo**. Tres pasos
separados y explícitos (nunca automáticos): (1) admin sube video → estado
`draft`, (2) admin ejecuta "procesar video" → genera plantilla de landmarks
(dataset), (3) admin cambia estado a `published` → solo entonces entra al
dataset de reconocimiento en vivo. Cada seña tiene `version` que se
incrementa explícitamente cuando el cambio lo amerita.

### Sección 13 — "AI Engine": abstracción obligatoria 🟢
> "el resto de la aplicación (servicios, API) depende únicamente de estas
> interfaces, nunca de una implementación concreta. Así, cambiar de motor de
> reconocimiento o síntesis de voz no requiere modificar los endpoints ni la
> lógica de negocio"
— `backend/app/ai/base.py:2-4`, replicado en `backend/app/ai/lsc/base.py:1-2`

Esta es la regla que el README actual preserva textualmente en su sección 5
("La abstracción `AI Engine`... debe mantenerse para poder cambiar modelos a
futuro") — confirma que el README sí heredó al menos esta regla completa.

### Sección 14-16 — ⚪
Sin rastro alguno.

### Sección 17 — Subtítulos en vivo durante la llamada 🟢
> "texto de apoyo en la videollamada"
— `frontend/flutter_app/lib/features/calls/call_screen.dart:29`, y
`frontend/flutter_app/lib/services/call_engine.dart:18`

Cada participante tiene su propio "caption" local y ve el del otro
(`localCaption` / `remoteCaption`).

### Sección 18 — ⚪
Sin rastro directo (posiblemente Docker/infraestructura general, ya que 19 es
específicamente Nginx).

### Sección 19 — Despliegue: HTTPS/WSS vía reverse proxy 🟢
> "configuración de Nginx como reverse proxy para el backend (HTTPS/WSS,
> sección 19) cuando el proyecto se despliegue en un servidor propio"
— `infrastructure/nginx/README.md:3-4`

### Sección 20 — Registro de modelos ORM / entidades nuevas 🟢
> "A medida que se agreguen nuevas entidades (Contacts, Calls, LSCSigns,
> etc. según la sección 20), deben importarse aquí también [en
> `models/__init__.py`]"
— `backend/app/models/__init__.py:5-6`

Regla operativa para Alembic/SQLAlchemy, no de producto.

### Sección 21 — Evolución de esquema sin romper compatibilidad 🟢
> "Esta tabla se ampliará en fases posteriores (más voces, más idiomas, etc.)
> sin romper la estructura actual"
— `backend/app/models/user_preferences.py:4-5`

### Sección 22 — Accesibilidad (UI) 🟢
Cuatro citas convergentes, todas del frontend Flutter:
> "Contraste alto entre texto y fondo (AA/AAA de WCAG donde es posible)"
> "Áreas táctiles grandes (mínimo 48x48 lógico) para botones"
> "Tipografía clara y tamaños base generosos"
> "Los estados... se comunican con color + ícono + texto, nunca solo con color"
— `frontend/flutter_app/lib/config/app_theme.dart:5-10`
> "permite escalar el texto del sistema sin romper el layout"
— `frontend/flutter_app/lib/main.dart:24`

Checklist de accesibilidad explícito y bastante completo — probablemente una
de las secciones más detalladas del documento original.

### Sección 23 — ⚪
Sin rastro (entre accesibilidad y criterios de IA — podría ser sobre el panel
de administración en general).

### Sección 24 — Criterio de selección de tecnología de IA (checklist) 🟢
Tres implementaciones de IA distintas (`landmark_extractor.py`,
`whisper_recognizer.py`, `espeak_synthesizer.py`) documentan su elección
usando **exactamente la misma estructura**, lo que confirma que la sección 24
definía un checklist obligatorio para justificar cualquier elección de motor
de IA:

- **Precisión**
- **Latencia**
- **Disponibilidad** (¿depende de internet/servicios pagos?)
- **Recursos de servidor** (CPU/GPU)
- **Entrenamiento** (¿se puede/necesita reentrenar?)
- **Licencia**
- **Integración** (facilidad de instalación/uso)
- **Escalabilidad**

Además: "no elegir tecnología solo por popularidad" —
`backend/app/ai/tts/espeak_synthesizer.py:2-3`.

### Sección 25 — Rendimiento: costo de cómputo acotado 🟢
> "muestreando a una tasa de frames objetivo para mantener el costo de
> cómputo acotado (sección 25: rendimiento)"
— `backend/app/ai/lsc/landmark_extractor.py:5-6`

### Sección 26 — Escalabilidad horizontal de servicios de IA 🟢
> "el extractor de landmarks se puede mover a un servicio de IA separado
> (sección 26) y escalar horizontalmente si el volumen crece"
— `backend/app/ai/lsc/landmark_extractor.py:16-17`, repetido para
Whisper (`whisper_recognizer.py:19-20`) y para el signaling
("Signaling Server" independiente con Redis pub/sub —
`backend/app/websocket/signaling_manager.py:14-16`).

### Sección 27 — ⚪
Sin rastro (entre escalabilidad y métricas de evaluación — candidato:
estrategia de testing/monitoreo).

### Sección 28 — Métricas de evaluación del modelo + expectativa de imperfección 🟢
> "Métricas: exactitud, precisión, recall, F1, latencia (sección 28)"
— `ai/README.md:9-10`
> "no asumir que el primer modelo será perfecto"
— `ai/README.md:15-16`, repetido en `backend/app/ai/lsc/dtw.py:8`

### Sección 29 — Nunca inventar: ni señas, ni reconocimientos, ni respuestas 🟢
La sección con más citas (5 en total) — regla central de integridad del
producto:
> "nunca se inventan señas. Cada registro representa material documentado" — `backend/app/models/lsc_sign.py:19`
> "se diferencia explícitamente palabra, seña, frase y estructura lingüística" — `backend/app/models/lsc_phrase.py:13-14`
> "no elegir tecnología... [ajustar] a medida que se acumulen más señas... en vez de arriesgar una respuesta incorrecta" — `backend/app/core/config.py:23-24`
> "Nunca 'inventa' una respuesta: si la mejor coincidencia [no] supera el umbral... se informa que no hubo reconocimiento en vez de devolver una seña incorrecta con falsa confianza" — `backend/app/services/lsc_recognition_service.py:26-29`
> "evita 'inventar' una seña con baja confianza" — `backend/tests/test_lsc_recognition.py:2`

Esta es probablemente **la regla de producto más importante** de todo el
documento original: preferir siempre "no sé" sobre una respuesta incorrecta,
tanto en contenido (no inventar señas que no estén documentadas) como en
inferencia (no devolver un match de baja confianza como si fuera certero).

### Sección 30-32 — ⚪ (con pista)
Sin cita numerada explícita, pero `avatar/README.md:6-7` dice:
> "Prioridad definida en la especificación: precisión del movimiento >
> claridad de las señas > sincronización > naturalidad > rendimiento"

Por posición (justo antes de la sección 33, sobre el avatar/Fase 6), es
probable que esta prioridad haya vivido en una de estas tres secciones sin
número confirmado.

### Sección 33 — Empezar simple antes de invertir en entrenamiento pesado 🟢
> "empezar simple antes de invertir en entrenamiento pesado"
— `backend/app/ai/lsc/dtw.py:9`

Justifica la elección de DTW (sin entrenamiento) sobre un modelo entrenado
(LSTM/Transformer) para la primera versión del reconocimiento.

### Sección 34+ — ⚪
Sin rastro de números más altos en el código actual. Es posible que las
"Reglas estrictas de desarrollo" del README (ramas `feature/`/`fix/`,
convención de commits, prohibición de tocar `main` directo) vinieran de una
sección tardía de la especificación (candidatos: 34-40), dado que el README
sí las preservó casi textuales.

---

## Huecos confirmados (sin ningún rastro en código)

`1, 7, 14, 15, 16, 18, 23, 27, 30, 31, 32` y todo lo que exista después de
`33` hasta el final real del documento (desconocido — pudo terminar en 34,
40, o más).

## Recomendación

1. **Preguntar primero** a los 3 (y a cualquier historial de chat con IA que
   haya generado el código original) antes de tratar esto como definitivo.
2. Si de verdad se perdió sin posibilidad de recuperación, usar este
   documento como base y **llenar los huecos en equipo** — sobre todo la
   sección 29 (nunca inventar) y la 24 (checklist de IA), que son las más
   accionables para las Fases 6-8 que faltan.
3. Una vez completado, mover este archivo a un nombre definitivo (p. ej.
   `ESPECIFICACION.md`) y **quitar las citas de línea de código** (quedan
   como prueba de reconstrucción, no como parte del documento final).
