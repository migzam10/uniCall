import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api_exception.dart';
import '../../core/providers.dart';
import '../../models/user_role.dart';

sealed class AuthState {
  const AuthState();
}

class AuthInitial extends AuthState {
  const AuthInitial();
}

class AuthLoading extends AuthState {
  const AuthLoading();
}

class AuthAuthenticated extends AuthState {
  const AuthAuthenticated();
}

class AuthUnauthenticated extends AuthState {
  const AuthUnauthenticated();
}

class AuthError extends AuthState {
  const AuthError(this.message);
  final String message;
}

class AuthController extends StateNotifier<AuthState> {
  AuthController(this._ref) : super(const AuthInitial()) {
    _checkSession();
  }

  final Ref _ref;

  Future<void> _checkSession() async {
    final hasSession = await _ref.read(authRepositoryProvider).hasActiveSession();
    state = hasSession ? const AuthAuthenticated() : const AuthUnauthenticated();
  }

  Future<void> login({required String usernameOrEmail, required String password}) async {
    state = const AuthLoading();
    try {
      await _ref.read(authRepositoryProvider).login(usernameOrEmail: usernameOrEmail, password: password);
      state = const AuthAuthenticated();
    } on ApiException catch (e) {
      state = AuthError(e.message);
    }
  }

  Future<void> register({
    required String fullName,
    required String username,
    required String email,
    required String password,
    required UserRole role,
  }) async {
    state = const AuthLoading();
    try {
      await _ref.read(authRepositoryProvider).register(
            fullName: fullName,
            username: username,
            email: email,
            password: password,
            role: role,
          );
      // Tras registrarse, el usuario inicia sesión explícitamente.
      state = const AuthUnauthenticated();
    } on ApiException catch (e) {
      state = AuthError(e.message);
    }
  }

  Future<void> logout() async {
    await _ref.read(authRepositoryProvider).logout();
    state = const AuthUnauthenticated();
  }
}

final authControllerProvider = StateNotifierProvider<AuthController, AuthState>(
  (ref) => AuthController(ref),
);
