import 'package:dio/dio.dart';

import '../core/api_client.dart';
import '../models/lsc_data.dart';

class LscAdminRepository {
  LscAdminRepository(this._apiClient);

  final ApiClient _apiClient;

  // --- Categorías ---

  Future<List<LscCategory>> listCategories() async {
    try {
      final response = await _apiClient.dio.get('/admin/lsc/categories');
      return (response.data as List).map((e) => LscCategory.fromJson(e)).toList();
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<LscCategory> createCategory(String name, String? description) async {
    try {
      final response =
          await _apiClient.dio.post('/admin/lsc/categories', data: {'name': name, 'description': description});
      return LscCategory.fromJson(response.data);
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<void> setCategoryActive(String categoryId, bool isActive) async {
    try {
      await _apiClient.dio.patch('/admin/lsc/categories/$categoryId', data: {'is_active': isActive});
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  // --- Señas ---

  Future<List<LscSign>> listSigns({String? categoryId}) async {
    try {
      final response = await _apiClient.dio.get(
        '/admin/lsc/signs',
        queryParameters: {if (categoryId != null) 'category_id': categoryId},
      );
      return (response.data as List).map((e) => LscSign.fromJson(e)).toList();
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<LscSignWithVideos> getSign(String signId) async {
    try {
      final response = await _apiClient.dio.get('/admin/lsc/signs/$signId');
      return LscSignWithVideos.fromJson(response.data);
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<LscSign> createSign({
    required String categoryId,
    required String word,
    required String meaning,
    String? description,
    String? tags,
  }) async {
    try {
      final response = await _apiClient.dio.post('/admin/lsc/signs', data: {
        'category_id': categoryId,
        'word': word,
        'meaning': meaning,
        'description': description,
        'tags': tags,
      });
      return LscSign.fromJson(response.data);
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<LscSign> updateSignStatus(String signId, {LscSignStatus? status, bool? bumpVersion, bool? isActive}) async {
    try {
      final response = await _apiClient.dio.patch('/admin/lsc/signs/$signId', data: {
        if (status != null) 'status': status.name,
        if (bumpVersion != null) 'bump_version': bumpVersion,
        if (isActive != null) 'is_active': isActive,
      });
      return LscSign.fromJson(response.data);
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  // --- Videos ---

  Future<LscVideo> uploadVideo(String signId, String filePath, String filename) async {
    try {
      final formData = FormData.fromMap({
        'video': await MultipartFile.fromFile(filePath, filename: filename),
      });
      final response = await _apiClient.dio.post('/admin/lsc/signs/$signId/videos', data: formData);
      return LscVideo.fromJson(response.data);
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<void> deleteVideo(String videoId) async {
    try {
      await _apiClient.dio.delete('/admin/lsc/videos/$videoId');
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  /// Extrae landmarks del video y los guarda como plantilla para el
  /// reconocimiento (Fase 5).
  Future<void> processVideo(String videoId) async {
    try {
      await _apiClient.dio.post('/admin/lsc/videos/$videoId/process');
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  // --- Frases ---

  Future<List<LscPhrase>> listPhrases() async {
    try {
      final response = await _apiClient.dio.get('/admin/lsc/phrases');
      return (response.data as List).map((e) => LscPhrase.fromJson(e)).toList();
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<LscPhrase> createPhrase(String text, String? description, List<Map<String, dynamic>> signs) async {
    try {
      final response = await _apiClient.dio.post('/admin/lsc/phrases', data: {
        'text': text,
        'description': description,
        'signs': signs,
      });
      return LscPhrase.fromJson(response.data);
    } on DioException catch (e) {
      throw _apiClient.mapError(e);
    }
  }
}
