/// Configuración de entorno de la aplicación.
///
/// Los valores se inyectan en tiempo de compilación, por ejemplo:
///   flutter run --dart-define-from-file=.env
///
/// Nunca se deben escribir URLs de producción ni credenciales directamente
/// en el código fuente.
class AppConfig {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://192.168.1.198:8100',
  );

  static const String wsBaseUrl = String.fromEnvironment(
    'WS_BASE_URL',
    defaultValue: 'ws://192.168.1.198:8100',
  );

  static const String apiV1 = '$apiBaseUrl/api/v1';
}
