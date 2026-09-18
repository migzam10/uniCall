import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../core/api_client.dart';
import '../core/token_storage.dart';
import '../repositories/auth_repository.dart';
import '../repositories/call_repository.dart';
import '../repositories/contact_repository.dart';
import '../repositories/lsc_admin_repository.dart';
import '../repositories/speech_repository.dart';
import '../repositories/user_repository.dart';

final secureStorageProvider = Provider<FlutterSecureStorage>((ref) => const FlutterSecureStorage());

final tokenStorageProvider = Provider<TokenStorage>((ref) => TokenStorage(ref.watch(secureStorageProvider)));

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient(ref.watch(tokenStorageProvider)));

final authRepositoryProvider = Provider<AuthRepository>(
  (ref) => AuthRepository(ref.watch(apiClientProvider), ref.watch(tokenStorageProvider)),
);

final userRepositoryProvider = Provider<UserRepository>(
  (ref) => UserRepository(ref.watch(apiClientProvider)),
);

final contactRepositoryProvider = Provider<ContactRepository>(
  (ref) => ContactRepository(ref.watch(apiClientProvider)),
);

final callRepositoryProvider = Provider<CallRepository>(
  (ref) => CallRepository(ref.watch(apiClientProvider)),
);

final speechRepositoryProvider = Provider<SpeechRepository>(
  (ref) => SpeechRepository(ref.watch(apiClientProvider)),
);

final lscAdminRepositoryProvider = Provider<LscAdminRepository>(
  (ref) => LscAdminRepository(ref.watch(apiClientProvider)),
);
