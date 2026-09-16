# PROYECTO: Plataforma de videollamadas accesibles con traducción de Lengua de Señas Colombiana

Quiero desarrollar una aplicación multiplataforma de videollamadas enfocada en facilitar la comunicación entre personas oyentes y personas sordas que utilizan la **Lengua de Señas Colombiana (LSC)**.

El sistema debe funcionar en:

* Android
* iOS
* Web

La aplicación debe utilizar **Flutter** para el frontend y un **backend propio desarrollado en Python** para los servicios del servidor y procesamiento de inteligencia artificial.

El objetivo principal es crear una plataforma de comunicación bidireccional en tiempo real:

**Persona oyente → habla → IA → LSC → avatar 3D → persona sorda**

y:

**Persona sorda → realiza señas → IA → español → voz → persona oyente**

El proyecto debe diseñarse desde el comienzo para ser escalable y permitir posteriormente incorporar nuevos idiomas y tecnologías de IA.

---

# 1. ARQUITECTURA GENERAL

Utilizar una arquitectura desacoplada y modular.

## Frontend

Utilizar:

* Flutter
* Dart

El mismo proyecto Flutter debe poder compilarse para:

* Android
* iOS
* Web

La interfaz debe ser responsive y adaptarse correctamente a teléfonos, tablets y computadores.

## Backend

Utilizar:

* Python
* API REST para operaciones generales
* WebSocket cuando sea necesario para comunicación en tiempo real
* WebRTC para audio y video
* Base de datos relacional
* Sistema de autenticación seguro

El backend debe estar preparado para ejecutarse en un servidor propio.

---

# 2. VIDEOLLAMADAS

Implementar videollamadas mediante **WebRTC**.

El audio y video de los participantes deben viajar preferentemente de forma directa entre los usuarios mediante WebRTC.

El servidor debe encargarse principalmente de:

* Señalización WebRTC.
* Autenticación.
* Gestión de usuarios.
* Contactos.
* Creación de llamadas.
* Códigos/enlaces de invitación.
* Estados de conexión.
* Servicios de inteligencia artificial.
* Traducción.
* Gestión de preferencias.
* Historial.
* Administración.

No convertir al servidor en un intermediario innecesario de todo el tráfico audiovisual.

Implementar los mecanismos necesarios de:

* STUN.
* TURN cuando sea necesario para usuarios detrás de NAT/firewalls.
* ICE.
* Cifrado WebRTC.
* Reconexión.
* Manejo de pérdida de conexión.
* Estados de llamada.

---

# 3. TIPOS DE USUARIO

La plataforma tendrá inicialmente tres tipos de cuenta:

## Usuario oyente

Puede:

* Realizar videollamadas.
* Recibir videollamadas.
* Hablar normalmente.
* Recibir traducción de LSC.
* Ver el texto interpretado.
* Escuchar la voz generada a partir de las señas.

## Usuario sordo

Puede:

* Realizar videollamadas.
* Recibir videollamadas.
* Utilizar la cámara para realizar LSC.
* Obtener interpretación de sus señas.
* Convertir sus señas en español hablado.
* Ver el texto interpretado.
* Controlar las opciones de traducción.

## Administrador

Puede:

* Administrar usuarios.
* Administrar contenido de LSC.
* Administrar vocabulario.
* Cargar videos de referencia.
* Administrar animaciones.
* Administrar categorías.
* Gestionar modelos/datos de IA.
* Revisar métricas del sistema.
* Administrar configuraciones.
* Gestionar permisos.

---

# 4. REGISTRO E INICIO DE SESIÓN

Crear sistema de cuentas.

Durante el registro solicitar:

* Nombre.
* Nombre de usuario.
* Correo electrónico.
* Contraseña.
* Tipo de usuario.
* Preferencias de comunicación.

El usuario podrá posteriormente modificar sus preferencias.

Implementar:

* Inicio de sesión.
* Cierre de sesión.
* Recuperación de contraseña.
* Verificación de cuenta cuando corresponda.
* Gestión de sesión.
* Tokens seguros.
* Control de permisos basado en roles.

No almacenar contraseñas en texto plano.

---

# 5. CONTACTOS

Los usuarios podrán:

* Buscar usuarios.
* Agregar contactos.
* Aceptar/rechazar solicitudes.
* Eliminar contactos.
* Ver contactos.
* Ver disponibilidad cuando sea posible.
* Iniciar videollamada directamente.

También debe existir la posibilidad de realizar una llamada sin tener previamente agregado al usuario.

---

# 6. LLAMADAS MEDIANTE CÓDIGO O ENLACE

El usuario podrá crear una llamada mediante:

* Código único.
* Enlace de invitación.

El sistema debe permitir:

1. Crear llamada.
2. Generar código/enlace.
3. Compartirlo.
4. El segundo usuario introduce el código o abre el enlace.
5. Se establece la conexión WebRTC.
6. Ambos usuarios entran a la videollamada.

Los códigos deben ser suficientemente aleatorios y contar con mecanismos de expiración cuando corresponda.

---

# 7. INTERFAZ DE VIDEOLLAMADA

Crear una interfaz moderna, sencilla y accesible.

Controles principales:

* Activar/desactivar micrófono.
* Activar/desactivar cámara.
* Cambiar cámara.
* Activar/desactivar traducción.
* Mostrar/ocultar texto.
* Mostrar/ocultar avatar.
* Activar/desactivar voz de traducción.
* Seleccionar voz masculina/femenina.
* Finalizar llamada.

La traducción debe iniciarse automáticamente según las preferencias del usuario, pero cada usuario debe poder modificarla manualmente.

---

# 8. SISTEMA DE TRADUCCIÓN BIDIRECCIONAL

Este es el componente central de la aplicación.

Debe existir un sistema de traducción en ambas direcciones.

## DIRECCIÓN 1

### Español hablado → LSC

Flujo:

```text
Micrófono
    ↓
Reconocimiento automático de voz
    ↓
Texto en español
    ↓
Procesamiento lingüístico
    ↓
Interpretación español → LSC
    ↓
Secuencia de LSC
    ↓
Biblioteca de animaciones
    ↓
Avatar humano 3D
    ↓
Persona sorda
```

Además del avatar, mostrar el texto correspondiente en pantalla.

No realizar una simple traducción palabra por palabra.

El sistema debe contemplar las diferencias estructurales entre español y LSC.

---

# 9. DIRECCIÓN 2

### LSC → español hablado

Flujo:

```text
Cámara
    ↓
Captura de video
    ↓
Procesamiento de visión artificial
    ↓
Detección de cuerpo, manos y rostro
    ↓
Modelo de reconocimiento de LSC
    ↓
Secuencia de señas
    ↓
Interpretación lingüística
    ↓
Español
    ↓
Texto
    ↓
Síntesis de voz
    ↓
Persona oyente
```

El sistema debe funcionar en tiempo real y tratar de mantener una latencia suficientemente baja para permitir una conversación natural.

---

# 10. RECONOCIMIENTO DE LSC

El sistema debe comenzar utilizando **Lengua de Señas Colombiana**.

No limitar el reconocimiento únicamente a manos.

El modelo debe poder considerar información como:

* Manos.
* Dedos.
* Brazos.
* Posición corporal.
* Movimiento.
* Rostro.
* Expresiones faciales.
* Cabeza.
* Orientación.
* Temporalidad del movimiento.

El reconocimiento debe trabajar con **secuencias de señas**, no únicamente con señas individuales.

Ejemplo conceptual:

```text
Seña 1
+
Seña 2
+
Seña 3
+
contexto
        ↓
interpretación
        ↓
frase en español
```

El modelo debe estar diseñado para procesar información temporal y contextual.

---

# 11. DATOS PARA ENTRENAMIENTO DE LSC

El proyecto debe incluir un sistema para administrar los datos de entrenamiento.

La fuente inicial será:

1. Manual/documentación de Lengua de Señas Colombiana.
2. Videos de referencia.

El manual se utilizará como fuente lingüística y documental.

Los videos serán utilizados como material visual para desarrollar y entrenar los modelos de reconocimiento.

Crear una estructura organizada por:

* Categorías.
* Palabras.
* Señas.
* Frases.
* Videos.
* Metadatos.

Ejemplo:

```text
LSC/
├── saludos/
│   ├── hola/
│   ├── buenos_dias/
│   └── buenas_noches/
├── personas/
├── lugares/
├── acciones/
├── objetos/
├── alimentos/
├── emociones/
└── frases/
```

El sistema debe permitir agregar posteriormente nuevas categorías y contenido.

---

# 12. PANEL DE ENTRENAMIENTO / DATOS

El administrador debe disponer de una sección para cargar material.

Debe poder:

* Crear categoría.
* Crear nueva seña.
* Asociar significado.
* Cargar video.
* Agregar descripción.
* Agregar etiquetas.
* Asociar la seña con palabras/frases.
* Revisar datos.
* Activar/desactivar registros.
* Versionar datos cuando sea necesario.

El sistema debe separar claramente:

**datos de entrenamiento**

de:

**modelo entrenado**

y:

**modelo utilizado en producción**.

No modificar directamente un modelo de producción sin un proceso controlado de validación.

---

# 13. MODELO DE IA

El backend debe estar preparado para trabajar con modelos de inteligencia artificial desarrollados en Python.

La arquitectura debe permitir reemplazar o actualizar el modelo sin tener que reconstruir toda la aplicación.

Crear una capa de abstracción similar a:

```text
AI Engine
├── Speech Recognition
├── LSC Recognition
├── Linguistic Translation
├── Text Processing
├── Speech Synthesis
└── Avatar Animation Mapping
```

La implementación concreta de cada modelo debe ser modular.

No acoplar la aplicación Flutter directamente al modelo de IA.

---

# 14. VOZ

Cuando una persona sorda utilice LSC, el sistema deberá convertir la interpretación a voz.

Inicialmente existirán dos opciones:

* Voz masculina.
* Voz femenina.

El usuario podrá seleccionar su preferencia.

La arquitectura debe permitir agregar posteriormente:

* Más voces.
* Otros idiomas.
* Diferentes configuraciones de pronunciación.

Inicialmente utilizar español colombiano.

---

# 15. AVATAR 3D

Utilizar un **avatar humano 3D realista**.

Debe existir inicialmente un único avatar estándar para todos los usuarios.

El avatar debe reproducir las animaciones correspondientes a LSC.

No se requiere inicialmente personalización de apariencia.

Prioridad:

1. Precisión del movimiento.
2. Claridad de las señas.
3. Sincronización.
4. Naturalidad.
5. Rendimiento.

---

# 16. BIBLIOTECA DE ANIMACIONES

Utilizar una biblioteca de animaciones LSC predefinidas.

Ejemplo conceptual:

```text
Animación:
"hola"

Animación:
"buenos_dias"

Animación:
"gracias"

Animación:
"cómo estás"
```

La IA debe identificar la estructura lingüística y posteriormente seleccionar las animaciones correspondientes.

La biblioteca debe ser ampliable.

El administrador debe poder gestionar:

* Animación.
* Nombre.
* Significado.
* Categoría.
* Seña asociada.
* Versión.
* Estado.
* Metadatos.

La precisión lingüística debe ser prioritaria.

---

# 17. TEXTO EN LA VIDEOLLAMADA

La aplicación debe mostrar texto de apoyo.

Ejemplo:

```text
Persona oyente:
"Buenos días, ¿cómo estás?"

          ↓

Avatar 3D:
[realiza las señas]

Texto:
"Buenos días, ¿cómo estás?"
```

En el sentido contrario:

```text
Persona sorda:
[realiza señas]

          ↓

Texto:
"Necesito ayuda"

          ↓

Voz:
"Necesito ayuda"
```

El usuario podrá activar/desactivar el texto.

---

# 18. HISTORIAL

Guardar un historial básico de llamadas.

Registrar:

* Contacto.
* Fecha.
* Hora.
* Duración.
* Llamada entrante.
* Llamada saliente.
* Llamada perdida.

No almacenar automáticamente grabaciones de audio/video.

El historial debe poder consultarse desde el perfil.

---

# 19. PRIVACIDAD Y SEGURIDAD

La aplicación debe tratar las comunicaciones como información privada.

Implementar:

* HTTPS.
* WSS.
* Autenticación segura.
* Autorización por roles.
* Protección de tokens.
* Cifrado de datos sensibles.
* Protección contra acceso no autorizado.
* Validación de entradas.
* Rate limiting.
* Protección de APIs.
* Gestión segura de sesiones.

No guardar audio/video de las llamadas salvo que en una futura versión se implemente explícitamente una función de grabación con consentimiento.

Diseñar el sistema teniendo en cuenta la legislación aplicable en Colombia sobre protección de datos personales.

---

# 20. BASE DE DATOS

Diseñar una base de datos relacional.

Como mínimo contemplar entidades para:

```text
Users
Profiles
Contacts
ContactRequests
Calls
CallParticipants
CallInvitations
LSCCategories
LSCSigns
LSCVideos
LSCAnimations
LSCPhrases
TrainingDatasets
AIModels
ModelVersions
VoiceSettings
UserPreferences
```

Diseñar correctamente las relaciones y utilizar migraciones.

---

# 21. MULTIIDIOMA

La primera versión trabajará con:

**Español colombiano + Lengua de Señas Colombiana.**

Sin embargo, la arquitectura debe quedar preparada para agregar posteriormente:

* Otros idiomas hablados.
* Otras lenguas de señas.

No implementar otros idiomas todavía salvo que sean necesarios para la arquitectura.

---

# 22. ACCESIBILIDAD

La aplicación debe estar diseñada desde el principio pensando en accesibilidad.

Utilizar:

* Contraste adecuado.
* Botones grandes.
* Iconografía clara.
* Texto legible.
* Indicadores visuales de estado.
* Indicadores visuales cuando el micrófono esté activo.
* Indicadores visuales cuando la cámara esté activa.
* Interfaz sencilla.
* Navegación intuitiva.

Evitar depender exclusivamente del audio para transmitir información importante.

---

# 23. ARQUITECTURA DEL PROYECTO

Organizar el proyecto de forma modular.

Proponer una estructura similar a:

```text
project/
│
├── frontend/
│   └── flutter_app/
│       ├── lib/
│       │   ├── core/
│       │   ├── config/
│       │   ├── models/
│       │   ├── services/
│       │   ├── repositories/
│       │   ├── features/
│       │   │   ├── auth/
│       │   │   ├── contacts/
│       │   │   ├── calls/
│       │   │   ├── translation/
│       │   │   ├── avatar/
│       │   │   ├── profile/
│       │   │   └── settings/
│       │   └── main.dart
│       └── test/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── websocket/
│   │   ├── webrtc/
│   │   ├── ai/
│   │   │   ├── speech/
│   │   │   ├── lsc/
│   │   │   ├── translation/
│   │   │   ├── tts/
│   │   │   └── avatar/
│   │   └── main.py
│   │
│   ├── tests/
│   └── requirements.txt
│
├── ai/
│   ├── datasets/
│   ├── preprocessing/
│   ├── training/
│   ├── evaluation/
│   ├── models/
│   └── notebooks/
│
├── avatar/
│   ├── models/
│   ├── animations/
│   └── metadata/
│
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   ├── turn/
│   └── deployment/
│
└── documentation/
```

La estructura final puede modificarse si existe una alternativa técnicamente superior.

---

# 24. TECNOLOGÍAS

Utilizar como base:

### Frontend

Flutter + Dart.

### Backend

Python.
FastAPI
Seleccionar un framework moderno de Python apropiado para APIs y comunicación asíncrona.

### Videollamada

WebRTC.

### Base de datos

Utilizar una base de datos relacional robusta.

### Comunicación en tiempo real

WebSocket cuando sea necesario.

### Contenedores

Utilizar Docker para facilitar el despliegue.

### Proxy

Utilizar un reverse proxy apropiado.

### IA

Utilizar herramientas y frameworks de Python adecuados para:

* Computer Vision.
* Deep Learning.
* Procesamiento de lenguaje natural.
* Reconocimiento de voz.
* Síntesis de voz.

La elección específica de modelos debe justificarse según:

* precisión;
* latencia;
* disponibilidad;
* recursos del servidor;
* posibilidad de entrenamiento;
* licencia;
* facilidad de integración;
* escalabilidad.

No elegir tecnologías solamente por popularidad.

---

# 25. RENDIMIENTO

La traducción debe intentar funcionar en tiempo real.

Optimizar:

* Latencia.
* Uso de CPU.
* Uso de GPU.
* Memoria.
* Ancho de banda.
* Procesamiento de video.
* Inferencia del modelo.

No enviar al servidor más información de la necesaria para realizar la inferencia.

Diseñar mecanismos de:

* buffering;
* procesamiento por frames;
* reducción de frames cuando sea necesario;
* batching cuando sea conveniente;
* aceleración mediante GPU;
* modelos optimizados.

---

# 26. ESCALABILIDAD

Aunque inicialmente el proyecto puede ejecutarse en un único servidor, diseñar la arquitectura para que posteriormente pueda crecer.

Separar conceptualmente:

```text
API Server
Signaling Server
AI Service
Database
Storage
TURN Server
Training Server
Avatar/Animation Service
```

No es obligatorio desplegar todos estos servicios separados en la primera versión.

La arquitectura debe permitir hacerlo posteriormente.

---

# 27. PANEL ADMINISTRATIVO

Crear un panel administrativo accesible desde Web.

Debe permitir:

### Usuarios

* Crear.
* Editar.
* Bloquear.
* Activar.
* Consultar.

### LSC

* Categorías.
* Señas.
* Frases.
* Videos.
* Animaciones.

### IA

* Datasets.
* Versiones.
* Modelos.
* Estado del entrenamiento.
* Métricas.
* Modelo actualmente activo.

### Sistema

* Configuración.
* Voces.
* Parámetros.
* Logs.
* Estado de servicios.

---

# 28. ENTRENAMIENTO

El sistema debe permitir una evolución progresiva.

Primera etapa:

```text
Manual LSC
     +
Videos de referencia
     ↓
Preparación de datos
     ↓
Etiquetado
     ↓
Preprocesamiento
     ↓
Entrenamiento
     ↓
Validación
     ↓
Evaluación
     ↓
Modelo
```

No considerar que el primer modelo será perfecto.

Implementar métricas para medir:

* Exactitud.
* Precisión.
* Recall.
* F1.
* Error de reconocimiento.
* Latencia.
* Calidad de traducción.

Mantener versiones de los modelos.

Permitir comparar un modelo nuevo con el modelo actualmente utilizado antes de ponerlo en producción.

---

# 29. IMPORTANTE SOBRE LSC

No inventar señas.

No asumir que una traducción literal español → LSC es lingüísticamente correcta.

El sistema debe estar diseñado para trabajar con material documentado de LSC.

Siempre que sea posible, los datos utilizados para definir las señas y animaciones deberán contar con validación lingüística adecuada.

El sistema debe diferenciar:

* significado;
* palabra;
* seña;
* variante;
* contexto;
* frase;
* estructura lingüística;
* animación.

---

# 30. EXPERIENCIA DEL USUARIO

La aplicación debe sentirse como una aplicación moderna de videollamadas, pero diseñada específicamente para comunicación accesible.

Pantallas principales:

1. Splash.
2. Inicio de sesión.
3. Registro.
4. Configuración inicial de accesibilidad.
5. Inicio.
6. Contactos.
7. Llamadas.
8. Crear llamada.
9. Unirse mediante código.
10. Videollamada.
11. Perfil.
12. Configuración.
13. Historial.
14. Panel administrativo.

---

# 31. DESARROLLO POR FASES

No intentar construir todo simultáneamente.

Dividir el proyecto en fases.

## Fase 1

Crear:

* Proyecto Flutter.
* Backend Python.
* Base de datos.
* Autenticación.
* Usuarios.
* Roles.
* Perfil.
* Configuración básica.

## Fase 2

Implementar:

* Contactos.
* Solicitudes.
* Llamadas.
* Código de llamada.
* WebRTC.
* Señalización.
* TURN/STUN.

## Fase 3

Implementar:

* Reconocimiento de voz.
* Texto.
* Síntesis de voz.
* Preferencias de voz.

## Fase 4

Implementar:

* Gestión de datos LSC.
* Carga de videos.
* Dataset.
* Procesamiento de datos.

## Fase 5

Implementar:

* Modelo inicial de reconocimiento de LSC.
* Inferencia.
* Integración con backend.

## Fase 6

Implementar:

* Biblioteca de animaciones.
* Avatar 3D.
* Traducción texto → LSC.
* Reproducción de animaciones.

## Fase 7

Integrar todo:

```text
WebRTC
+
voz
+
LSC
+
IA
+
texto
+
avatar
+
voz sintetizada
```

## Fase 8

Pruebas:

* Funcionales.
* Rendimiento.
* Latencia.
* Seguridad.
* Compatibilidad Android.
* Compatibilidad iOS.
* Compatibilidad Web.
* Pruebas de reconocimiento.
* Pruebas de traducción.

---

# 32. REGLAS PARA LA IA DE PROGRAMACIÓN

No generar todo el proyecto de manera desordenada.

Primero crear la arquitectura.

Después implementar cada módulo.

Antes de comenzar cada fase:

1. Explicar qué se va a construir.
2. Crear los archivos necesarios.
3. Implementar.
4. Ejecutar pruebas.
5. Corregir errores.
6. Documentar.
7. Continuar con la siguiente fase.

No eliminar funcionalidades existentes al agregar nuevas.

Mantener código limpio, modular y documentado.

Utilizar variables de entorno para secretos y credenciales.

No colocar claves API directamente en el código.

Crear archivos `.env.example`.

Agregar pruebas automatizadas donde sea apropiado.

Crear documentación para instalación y despliegue.

---

# 33. OBJETIVO FINAL

El resultado debe ser una plataforma de videollamadas accesible en la que una persona oyente y una persona sorda puedan mantener una conversación prácticamente en tiempo real utilizando sus formas naturales de comunicación.

### Persona oyente

Habla normalmente:

```text
Voz
 ↓
Reconocimiento de voz
 ↓
Español
 ↓
Interpretación lingüística
 ↓
LSC
 ↓
Avatar 3D
```

### Persona sorda

Realiza LSC:

```text
Cámara
 ↓
Visión artificial
 ↓
Reconocimiento de secuencia LSC
 ↓
Interpretación lingüística
 ↓
Español
 ↓
Texto
 ↓
Voz
```

La aplicación debe priorizar:

**accesibilidad + precisión lingüística + baja latencia + privacidad + escalabilidad.**

No simplificar el proyecto reduciéndolo a un traductor de palabras individuales. El objetivo es desarrollar progresivamente un sistema capaz de interpretar **secuencias y frases en Lengua de Señas Colombiana**.

Comenzar por la arquitectura y la primera fase funcional. No intentar implementar el entrenamiento completo de IA antes de tener preparada la infraestructura de datos, validación y pruebas.