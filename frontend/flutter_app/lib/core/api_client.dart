import 'package:dio/dio.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';

import '../config/app_config.dart';
import 'api_exception.dart';
import 'token_storage.dart';

/// Cliente HTTP centralizado.
///
/// - Agrega el access token a cada request autenticada.
/// - Si el backend responde 401, intenta refrescar el token una vez y
///   reintenta la petición original antes de forzar logout.
/// - Traduce errores de Dio a [ApiException] para que la UI no dependa
///   de detalles de la librería HTTP.
class ApiClient {
  ApiClient(this._tokenStorage) : dio = Dio(BaseOptions(baseUrl: AppConfig.apiV1)) {
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _tokenStorage.getAccessToken();
          if (token != null && !options.path.contains('/auth/')) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401 && !_isRefreshing) {
            final refreshed = await _tryRefreshToken();
            if (refreshed) {
              final cloned = await _retry(error.requestOptions);
              return handler.resolve(cloned);
            }
          }
          handler.next(error);
        },
      ),
    );

    if (AppConfig.apiBaseUrl.contains('localhost') || AppConfig.apiBaseUrl.contains('127.0.0.1')) {
      dio.interceptors.add(PrettyDioLogger(requestBody: true, responseBody: true));
    }
  }

  final Dio dio;
  final TokenStorage _tokenStorage;
  bool _isRefreshing = false;

  Future<bool> _tryRefreshToken() async {
    _isRefreshing = true;
    try {
      final refreshToken = await _tokenStorage.getRefreshToken();
      if (refreshToken == null) return false;

      final response = await dio.post('/auth/refresh', data: {'refresh_token': refreshToken});
      await _tokenStorage.saveTokens(
        accessToken: response.data['access_token'],
        refreshToken: response.data['refresh_token'],
      );
      return true;
    } catch (_) {
      await _tokenStorage.clear();
      return false;
    } finally {
      _isRefreshing = false;
    }
  }

  Future<Response<dynamic>> _retry(RequestOptions requestOptions) async {
    final token = await _tokenStorage.getAccessToken();
    final options = Options(method: requestOptions.method, headers: {'Authorization': 'Bearer $token'});
    return dio.request<dynamic>(
      requestOptions.path,
      data: requestOptions.data,
      queryParameters: requestOptions.queryParameters,
      options: options,
    );
  }

  /// Convierte un [DioException] en [ApiException] con un mensaje legible.
  ApiException mapError(DioException error) {
    final statusCode = error.response?.statusCode;
    final data = error.response?.data;
    String message = 'Ocurrió un error de conexión. Intenta nuevamente.';

    if (data is Map && data['detail'] is String) {
      message = data['detail'] as String;
    } else if (statusCode == 401) {
      message = 'Sesión expirada. Inicia sesión nuevamente.';
    } else if (statusCode == 403) {
      message = 'No tienes permisos para realizar esta acción.';
    }

    return ApiException(statusCode: statusCode, message: message);
  }
}
