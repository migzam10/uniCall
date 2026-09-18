# Permisos nativos para videollamadas (WebRTC)

Este proyecto Flutter fue generado como código fuente (`lib/`, `pubspec.yaml`,
`test/`) sin las carpetas nativas de plataforma (`android/`, `ios/`, `web/`,
etc.), porque esas carpetas las genera el propio SDK de Flutter y no había
acceso a él en el entorno donde se construyó este proyecto.

## Paso 1: generar las carpetas de plataforma

Dentro de `frontend/flutter_app`, con el SDK de Flutter instalado:

```bash
flutter create . --platforms=android,ios,web
```

Esto genera `android/`, `ios/` y `web/` sin sobrescribir tu `lib/` ni tu
`pubspec.yaml` existentes (Flutter detecta que ya hay un proyecto Dart ahí).

## Paso 2: agregar permisos de cámara y micrófono

`flutter_webrtc` (usado para las videollamadas) necesita acceso a cámara y
micrófono. Agrega lo siguiente después de generar las carpetas:

### Android — `android/app/src/main/AndroidManifest.xml`

Dentro de la etiqueta `<manifest>`, antes de `<application>`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
<uses-permission android:name="android.permission.BLUETOOTH" />
<uses-feature android:name="android.hardware.camera" />
<uses-feature android:name="android.hardware.camera.autofocus" />
```

En `android/app/build.gradle`, asegúrate de que `minSdkVersion` sea al menos
`24` (requisito de `flutter_webrtc`).

### iOS — `ios/Runner/Info.plist`

Dentro del diccionario principal `<dict>`:

```xml
<key>NSCameraUsageDescription</key>
<string>Necesitamos la cámara para tus videollamadas y para interpretar Lengua de Señas Colombiana.</string>
<key>NSMicrophoneUsageDescription</key>
<string>Necesitamos el micrófono para tus videollamadas.</string>
```

### Web

No se requiere configuración adicional: el navegador pedirá permiso de
cámara/micrófono automáticamente. Ten en cuenta que **WebRTC en la mayoría
de navegadores solo funciona sobre HTTPS o `localhost`** — para probar en
un dispositivo físico en la misma red, necesitarás servir la app por HTTPS
o usar `flutter run -d chrome` en la misma máquina.

## Paso 3: verificar

```bash
flutter pub get
flutter analyze
flutter test
flutter run -d chrome --dart-define-from-file=.env
```

## Nota sobre grabación de voz (STT, Fase 3)

El paquete `record`, usado para grabar la voz de la persona oyente y
enviarla a transcribir, **reutiliza los mismos permisos de micrófono**
agregados arriba (`RECORD_AUDIO` en Android, `NSMicrophoneUsageDescription`
en iOS). No se necesita ningún permiso adicional.
