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
    defaultValue: 'http://localhost:8000',
  );

  static const String wsBaseUrl = String.fromEnvironment(
    'WS_BASE_URL',
    defaultValue: 'ws://localhost:8000',
  );

  static const String apiV1 = '$apiBaseUrl/api/v1';
}
