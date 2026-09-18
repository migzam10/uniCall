/// Excepción de dominio para errores devueltos por el backend.
///
/// Traduce respuestas HTTP a mensajes que la UI puede mostrar directamente,
/// sin acoplar las pantallas a detalles de Dio/HTTP.
class ApiException implements Exception {
  ApiException({required this.statusCode, required this.message});

  final int? statusCode;
  final String message;

  bool get isUnauthorized => statusCode == 401;
  bool get isForbidden => statusCode == 403;
  bool get isConflict => statusCode == 409;
  bool get isNotFound => statusCode == 404;

  @override
  String toString() => message;
}
