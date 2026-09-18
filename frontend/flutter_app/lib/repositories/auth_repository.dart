import 'package:dio/dio.dart';

import '../core/api_client.dart';
import '../core/token_storage.dart';
import '../models/user_role.dart';

class AuthRepository {
  AuthRepository(this._apiClient, this._tokenStorage);

  final ApiClient _apiClient;
  final TokenStorage _tokenStorage;

  Future<void> register({
    required String fullName,
    required String username,
    required String email,
    required String password,
    required UserRole role,
  }) async {
    try {
      await _apiClient.dio.post('/auth/register', data: {
        'full_name': fullName,
        'username': username,
        'email': email,
        'password': password,
        'role': role.toJson(),
      });
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<void> login({required String usernameOrEmail, required String password}) async {
    try {
      final response = await _apiClient.dio.post('/auth/login', data: {
        'username_or_email': usernameOrEmail,
        'password': password,
      });
      await _tokenStorage.saveTokens(
        accessToken: response.data['access_token'],
        refreshToken: response.data['refresh_token'],
      );
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<void> logout() async {
    try {
      await _apiClient.dio.post('/auth/logout');
    } catch (_) {
      // El logout es best-effort del lado del servidor; el token local
      // siempre se limpia a continuación.
    } finally {
      await _tokenStorage.clear();
    }
  }

  Future<bool> hasActiveSession() => _tokenStorage.hasSession();
}
