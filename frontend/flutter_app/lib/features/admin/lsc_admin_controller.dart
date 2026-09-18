import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/providers.dart';
import '../../models/lsc_data.dart';

final lscCategoriesProvider = FutureProvider.autoDispose<List<LscCategory>>((ref) async {
  return ref.watch(lscAdminRepositoryProvider).listCategories();
});

final lscSignsProvider = FutureProvider.autoDispose.family<List<LscSign>, String?>((ref, categoryId) async {
  return ref.watch(lscAdminRepositoryProvider).listSigns(categoryId: categoryId);
});

final lscSignDetailProvider = FutureProvider.autoDispose.family<LscSignWithVideos, String>((ref, signId) async {
  return ref.watch(lscAdminRepositoryProvider).getSign(signId);
});

final lscPhrasesProvider = FutureProvider.autoDispose<List<LscPhrase>>((ref) async {
  return ref.watch(lscAdminRepositoryProvider).listPhrases();
});
