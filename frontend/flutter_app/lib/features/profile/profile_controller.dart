import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/providers.dart';
import '../../repositories/user_repository.dart';

final meProvider = FutureProvider.autoDispose<MeData>((ref) async {
  return ref.watch(userRepositoryProvider).getMe();
});
